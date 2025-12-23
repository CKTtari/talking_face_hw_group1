// 训练页面脚本

// 全局变量，用于存储上传的文件对象
let uploadedVideoFile = null;
let uploadedAudioFile = null;

// 页面加载时获取GPU信息
window.addEventListener('DOMContentLoaded', function() {
    loadGPUInfo();
});

// 加载GPU信息
function loadGPUInfo() {
    fetch('/api/gpu_info')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateGPUOptions(data.gpus);
            } else {
                console.error('获取GPU信息失败:', data.error);
                // 使用默认选项
                updateGPUOptions([
                    {id: 'GPU0', name: '默认GPU', memory_total: '未知', memory_free: '未知', available: true},
                    {id: 'CPU', name: 'CPU模式', memory_total: '系统内存', memory_free: '未知', available: true}
                ]);
            }
        })
        .catch(error => {
            console.error('获取GPU信息出错:', error);
            // 使用默认选项
            updateGPUOptions([
                {id: 'GPU0', name: '默认GPU', memory_total: '未知', memory_free: '未知', available: true},
                {id: 'CPU', name: 'CPU模式', memory_total: '系统内存', memory_free: '未知', available: true}
            ]);
        });
}

// 更新GPU选择框选项
function updateGPUOptions(gpus) {
    const gpuSelect = document.getElementById('gpuSelect');
    if (!gpuSelect) return;
    
    // 清空现有选项
    gpuSelect.innerHTML = '';
    
    // 添加新的GPU选项
    gpus.forEach(gpu => {
        const option = document.createElement('option');
        option.value = gpu.id;
        option.textContent = `${gpu.id} - ${gpu.name} (${gpu.memory_total}, 可用: ${gpu.memory_free})`;
        option.disabled = !gpu.available;
        
        if (gpu.id === 'GPU0') {
            option.selected = true;
        }
        
        gpuSelect.appendChild(option);
    });
    
    // 如果没有GPU0，选择第一个可用的GPU
    if (!gpuSelect.value) {
        const firstAvailable = gpuSelect.querySelector('option:not([disabled])');
        if (firstAvailable) {
            firstAvailable.selected = true;
        }
    }
}

// 上传文件
function uploadFile(type) {
    const input = document.createElement('input');
    input.type = 'file';
    
    if (type === 'video') {
        input.accept = 'video/*';
    } else if (type === 'audio') {
        input.accept = 'audio/*';
    }
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (type === 'video') {
                uploadedVideoFile = file;
                document.getElementById('referenceVideo').value = file.name;
            } else if (type === 'audio') {
                uploadedAudioFile = file;
                document.getElementById('referenceAudio').value = file.name;
            }
            showNotification('文件已选择：' + file.name, 'success');
        }
    };
    
    input.click();
}

// 开始训练
function startTraining() {
    const modelName = document.getElementById('modelName').value;
    const gpu = document.getElementById('gpuSelect').value;
    const epochs = document.getElementById('epochs').value;
    
    // 获取自定义参数
    const maxUpdates = document.getElementById('maxUpdates').value;
    const speakerName = document.getElementById('speakerName').value;
    const torsoCkpt = document.getElementById('torsoCkpt').value;
    const batchSize = document.getElementById('batchSize').value;
    const lr = document.getElementById('lr').value;
    const lrTriplane = document.getElementById('lrTriplane').value;
    
    // 构建自定义参数JSON
    const customParamsObj = {
        max_updates: parseInt(maxUpdates),
        speaker_name: speakerName || null,
        torso_ckpt: torsoCkpt,
        batch_size: parseInt(batchSize),
        lr: parseFloat(lr),
        lr_triplane: parseFloat(lrTriplane)
    };
    
    // 过滤掉空值和默认值（可选）
    const filteredParams = {};
    for (const [key, value] of Object.entries(customParamsObj)) {
        if (value !== null && value !== undefined && value !== '') {
            filteredParams[key] = value;
        }
    }
    
    const customParams = JSON.stringify(filteredParams);
    
    if (!uploadedVideoFile) {
        showNotification('请上传参考视频', 'error');
        return;
    }
    
    const trainButton = document.querySelector('.btn-train');
    trainButton.disabled = true;
    trainButton.textContent = '训练中...';
    
    // 显示进度条
    const progressBar = document.getElementById('progressBar');
    progressBar.style.display = 'block';
    
    // 创建表单数据，直接上传文件
    const formData = new FormData();
    formData.append('reference_video', uploadedVideoFile);
    formData.append('model_name', modelName);
    formData.append('gpu', gpu);
    formData.append('epochs', epochs);
    formData.append('custom_params', customParams);
    
    // 调用训练API
    fetch('/api/train', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('训练已启动', 'success');
            monitorTrainingProgress(data.task_id);
        } else {
            showNotification('启动失败: ' + data.error, 'error');
            trainButton.disabled = false;
            trainButton.textContent = '开始训练';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('请求出错: ' + error.message, 'error');
        trainButton.disabled = false;
        trainButton.textContent = '开始训练';
    });
}

// 监控训练进度
function monitorTrainingProgress(taskId) {
    const pollInterval = setInterval(() => {
        fetch(`/api/task/${taskId}`)
        .then(response => response.json())
        .then(task => {
            if (task.error) {
                clearInterval(pollInterval);
                showNotification('任务查询失败', 'error');
                return;
            }
            
            // 更新进度条
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            progressFill.style.width = task.progress + '%';
            progressText.textContent = task.progress + '%';
            
            // 训练完成
            if (task.status === 'completed') {
                clearInterval(pollInterval);
                if (task.video_url) {
                    displayVideo(task.video_url);
                }
                showNotification('训练完成！', 'success');
                document.querySelector('.btn-train').disabled = false;
                document.querySelector('.btn-train').textContent = '开始训练';
            } else if (task.status === 'error') {
                clearInterval(pollInterval);
                showNotification('训练出错', 'error');
                document.querySelector('.btn-train').disabled = false;
                document.querySelector('.btn-train').textContent = '开始训练';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }, 1000);
}

// 显示视频
function displayVideo(videoUrl) {
    const videoDisplay = document.getElementById('videoDisplay');
    videoDisplay.innerHTML = `<video controls><source src="${videoUrl}" type="video/mp4">Your browser does not support the video tag.</video>`;
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    `;
    
    if (type === 'success') {
        notification.style.background = '#4caf50';
    } else if (type === 'error') {
        notification.style.background = '#f44336';
    } else {
        notification.style.background = '#2196f3';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(300px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(300px);
        }
    }
`;
document.head.appendChild(style);