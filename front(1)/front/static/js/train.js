// 训练页面脚本

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
            uploadToServer(file, type);
        }
    };
    
    input.click();
}

// 上传文件到服务器
function uploadToServer(file, type) {
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (type === 'video') {
                document.getElementById('referenceVideo').value = data.path;
            } else if (type === 'audio') {
                document.getElementById('referenceAudio').value = data.path;
            }
            showNotification('文件上传成功', 'success');
        } else {
            showNotification('文件上传失败: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('上传出错: ' + error.message, 'error');
    });
}

// 开始训练
function startTraining() {
    const modelName = document.getElementById('modelName').value;
    const referenceVideo = document.getElementById('referenceVideo').value;
    const gpu = document.getElementById('gpuSelect').value;
    const epochs = document.getElementById('epochs').value;
    const customParams = document.getElementById('customParams').value;
    
    if (!referenceVideo) {
        showNotification('请输入或上传参考视频地址', 'error');
        return;
    }
    
    const trainButton = document.querySelector('.btn-train');
    trainButton.disabled = true;
    trainButton.textContent = '训练中...';
    
    // 显示进度条
    const progressBar = document.getElementById('progressBar');
    progressBar.style.display = 'block';
    
    const data = {
        model_name: modelName,
        reference_video: referenceVideo,
        gpu: gpu,
        epochs: parseInt(epochs),
        custom_params: customParams
    };
    
    fetch('/api/train', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
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
