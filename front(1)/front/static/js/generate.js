// 视频生成页面脚本

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

// 选择目录
function selectDirectory() {
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;
    
    input.onchange = (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            const dirPath = files[0].webkitRelativePath.split('/')[0];
            document.getElementById('modelDir').value = dirPath;
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
            if (type === 'audio') {
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

// 生成视频
function generateVideo() {
    const modelName = document.getElementById('modelName').value;
    const modelDir = document.getElementById('modelDir').value;
    const referenceAudio = document.getElementById('referenceAudio').value;
    const gpu = document.getElementById('gpuSelect').value;
    const voiceCloneModel = document.getElementById('voiceCloneModel').value;
    const targetText = document.getElementById('targetText').value;
    
    if (!modelDir || !referenceAudio || !targetText) {
        showNotification('请填写所有必填字段', 'error');
        return;
    }
    
    const generateButton = document.querySelector('.btn-generate');
    generateButton.disabled = true;
    generateButton.textContent = '生成中...';
    
    // 显示进度条
    const progressBar = document.getElementById('progressBar');
    progressBar.style.display = 'block';
    
    const data = {
        model_name: modelName,
        model_dir: modelDir,
        reference_audio: referenceAudio,
        gpu: gpu,
        voice_clone_model: voiceCloneModel,
        target_text: targetText,
        pitch: parseInt(document.getElementById('pitchControl') ? document.getElementById('pitchControl').value : 0),
        tfg_remove_bg: document.getElementById('tfgRemoveBg') ? document.getElementById('tfgRemoveBg').checked : false
    };
    
    fetch('/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('视频生成已启动', 'success');
            monitorGenerationProgress(data.task_id);
        } else {
            showNotification('启动失败: ' + data.error, 'error');
            generateButton.disabled = false;
            generateButton.textContent = '生成视频';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('请求出错: ' + error.message, 'error');
        generateButton.disabled = false;
        generateButton.textContent = '生成视频';
    });
}

// 监控生成进度
function monitorGenerationProgress(taskId) {
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
            
            // 生成完成
            if (task.status === 'completed') {
                clearInterval(pollInterval);
                if (task.video_url) {
                    displayVideo(task.video_url);
                }
                showNotification('视频生成完成！', 'success');
                document.querySelector('.btn-generate').disabled = false;
                document.querySelector('.btn-generate').textContent = '生成视频';
            } else if (task.status === 'error') {
                clearInterval(pollInterval);
                showNotification('生成出错', 'error');
                document.querySelector('.btn-generate').disabled = false;
                document.querySelector('.btn-generate').textContent = '生成视频';
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
