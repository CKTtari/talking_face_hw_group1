// 视频生成页面脚本

// 全局变量，用于存储上传的文件对象
let uploadedAudioFile = null;
let uploadedVideoFile = null;

// 添加模拟进度变量
let simulateProgress = 0;
let simulateProgressInterval = null;

// 页面加载时获取GPU信息和保存的模型目录
window.addEventListener('DOMContentLoaded', function() {
    loadGPUInfo();
    // 从localStorage获取保存的模型目录地址
    const savedModelDir = localStorage.getItem('modelDir');
    if (savedModelDir) {
        document.getElementById('modelDir').value = savedModelDir;
    }
    
    // 初始化滑块控件
    initControls();
});

// 初始化控件
function initControls() {
    // 音频升降调滑块
    const pitchControl = document.getElementById('pitchControl');
    const pitchValue = document.getElementById('pitchValue');
    if (pitchControl && pitchValue) {
        pitchControl.addEventListener('input', function() {
            pitchValue.textContent = this.value;
        });
    }
    
    // 视频加速减速滑块
    const speedControl = document.getElementById('speedControl');
    const speedValue = document.getElementById('speedValue');
    if (speedControl && speedValue) {
        speedControl.addEventListener('input', function() {
            speedValue.textContent = this.value;
        });
    }
}

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
    
    if (type === 'audio') {
        input.accept = 'audio/*';
    } else if (type === 'video') {
        input.accept = 'video/*';
    }
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (type === 'audio') {
                uploadedAudioFile = file;
                document.getElementById('referenceAudio').value = file.name;
            } else if (type === 'video') {
                uploadedVideoFile = file;
                document.getElementById('referenceVideo').value = file.name;
            }
            showNotification('文件已选择：' + file.name, 'success');
        }
    };
    
    input.click();
}

// 选择目录
function selectDirectory() {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.webkitdirectory = true;
    
    input.onchange = (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            // 获取目录名
            const dirPath = files[0].webkitRelativePath.split('/')[0];
            
            // 弹出提示，说明浏览器安全限制导致无法获取完整路径
            alert(`已识别到目录: ${dirPath}\n\n由于浏览器安全限制，我们无法获取完整路径。请直接在输入框中输入完整的模型目录路径，例如：E:\\projects\\MimicTalk\\checkpoints_mimictalk\\${dirPath}`);
            
            // 保留自动填充的目录名，用户可以手动修改为完整路径
            document.getElementById('modelDir').value = dirPath;
            console.log('目录已选择:', dirPath);
        }
    };
    
    input.click();
}

// 生成视频
function generateVideo() {
    const targetText = document.getElementById('targetText').value;
    const modelDir = document.getElementById('modelDir').value;
    const modelName = document.getElementById('modelName').value;
    const gpu = document.getElementById('gpuSelect').value;
    const pitch = document.getElementById('pitchControl').value;
    const speed = document.getElementById('speedControl').value;
    
    if (!uploadedAudioFile || !uploadedVideoFile || !modelDir) {
        showNotification('请上传音频和视频文件并选择模型目录', 'error');
        return;
    }
    
    // 保存模型目录地址
    localStorage.setItem('modelDir', modelDir);
    
    const generateButton = document.querySelector('.btn-generate');
    generateButton.disabled = true;
    generateButton.textContent = '生成中...';
    
    // 显示进度条
    const progressBar = document.getElementById('progressBar');
    progressBar.style.display = 'block';
    
    // 设置进度条初始值
    updateProgressBar(0);
    
    // 开始模拟进度增长
    simulateProgress = 0;
    startSimulateProgress();
    
    // 创建表单数据，直接上传文件
    const formData = new FormData();
    formData.append('reference_audio', uploadedAudioFile);
    formData.append('reference_video', uploadedVideoFile);
    formData.append('model_dir', modelDir);
    formData.append('model_name', modelName);
    formData.append('gpu', gpu);
    formData.append('target_text', targetText);
    formData.append('pitch', pitch);
    formData.append('speed', speed);
    
    // 调用生成API
    fetch('/api/generate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('视频生成已启动', 'success');
            monitorGenerationProgress(data.task_id);
        } else {
            // 停止模拟进度增长
            stopSimulateProgress();
            
            showNotification('启动失败: ' + data.error, 'error');
            generateButton.disabled = false;
            generateButton.textContent = '生成视频';
            progressBar.style.display = 'none';
        }
    })
    .catch(error => {
        // 停止模拟进度增长
        stopSimulateProgress();
        
        console.error('请求出错:', error);
        showNotification('请求出错: ' + error.message, 'error');
        generateButton.disabled = false;
        generateButton.textContent = '生成视频';
        progressBar.style.display = 'none';
    });
}

// 开始模拟进度增长
function startSimulateProgress() {
    // 清除可能存在的旧定时器
    stopSimulateProgress();
    
    // 设置模拟进度初始值
    simulateProgress = 0;
    
    // 每100ms更新一次模拟进度
    simulateProgressInterval = setInterval(() => {
        // 每次增加剩余进度的1%
        const remainingProgress = 100 - simulateProgress;
        simulateProgress += remainingProgress * 0.001;
        // 确保进度不会超过99%
        simulateProgress = Math.min(99, simulateProgress);
        // 更新进度条
        updateProgressBar(simulateProgress);
    }, 100);
}

// 停止模拟进度增长
function stopSimulateProgress() {
    if (simulateProgressInterval) {
        clearInterval(simulateProgressInterval);
        simulateProgressInterval = null;
    }
}

// 更新进度条
function updateProgressBar(progress) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const integerProgress = Math.floor(progress);
    progressFill.style.width = integerProgress + '%';
    progressText.textContent = integerProgress + '%';
}

// 监控生成进度
function monitorGenerationProgress(taskId) {
    const generateButton = document.querySelector('.btn-generate');
    const progressBar = document.getElementById('progressBar');
    
    // 使用setInterval定期查询进度
    const intervalId = setInterval(() => {
        fetch(`/api/task/${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    clearInterval(intervalId);
                    showNotification('任务查询失败: ' + data.error, 'error');
                    generateButton.disabled = false;
                    generateButton.textContent = '生成视频';
                    progressBar.style.display = 'none';
                    return;
                }
                
                // 更新进度条
                updateProgressBar(data.progress);
                
                // 更新状态信息
                const statusInfo = document.getElementById('statusInfo');
                if (statusInfo) {
                    statusInfo.textContent = `状态: ${data.status} | 进度: ${data.progress}%`;
                }
                
                // 检查任务是否完成
                if (data.status === 'completed') {
                    clearInterval(intervalId);
                    if (data.video_url) {
                        displayVideo(data.video_url);
                    }
                    showNotification('视频生成完成！', 'success');
                    generateButton.disabled = false;
                    generateButton.textContent = '生成视频';
                    progressBar.style.display = 'none';
                } else if (data.status === 'error' || data.status === 'failed') {
                    clearInterval(intervalId);
                    showNotification('生成出错: ' + (data.error || '未知错误'), 'error');
                    generateButton.disabled = false;
                    generateButton.textContent = '生成视频';
                    progressBar.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('查询进度出错:', error);
                clearInterval(intervalId);
                showNotification('查询进度出错: ' + error.message, 'error');
                generateButton.disabled = false;
                generateButton.textContent = '生成视频';
                progressBar.style.display = 'none';
            });
    }, 1000); // 每1秒查询一次
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