// 实时对话页面脚本

// 上传文件
function uploadFile(type) {
    const input = document.createElement('input');
    input.type = 'file';
    
    if (type === 'audio') {
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

let chatActive = false;
let characterVideoPlaying = false;

// 当将来需要把 pitch 一并发给后端时，可使用此函数获取值
function getChatPitch() {
    const el = document.getElementById('pitchControl');
    return el ? parseInt(el.value) : 0;
}

// 更新对话按钮状态
function updateChatButton() {
    const btn = document.getElementById('chatToggleBtn');
    if (btn) {
        if (chatActive) {
            btn.textContent = '停止对话';
            btn.className = 'btn-stop';
        } else {
            btn.textContent = '开始对话';
            btn.className = 'btn-primary';
        }
    }
}

// 开始对话
function startChat() {
    if (chatActive) {
        showNotification('对话已经在进行中', 'info');
        return;
    }
    
    chatActive = true;
    
    // 获取用户摄像头和麦克风权限
    WebRTC.startLocalVideo('userVideo');
    
    // 模拟连接克隆人物视频
    connectCharacterVideo();
    
    // 更新按钮状态
    updateChatButton();
    
    showNotification('对话已开始', 'success');
}

// 添加消息到聊天窗口
function addMessage(message, sender) {
    const chatMessages = document.querySelector('.chat-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender}`;
    
    const timestamp = new Date().toLocaleTimeString('zh-CN');
    messageElement.innerHTML = `
        ${message}
        <div class="chat-timestamp">${timestamp}</div>
    `;
    
    chatMessages.appendChild(messageElement);
    
    // 自动滚动到底部
    const chatDisplay = document.getElementById('chatDisplay');
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

// 播放角色回应
function playCharacterResponse() {
    const characterVideo = document.getElementById('characterVideo');
    // 这里应该播放与bot回应相对应的视频
    // 现在只是显示一个占位符
    const video = characterVideo.querySelector('video');
    if (video) {
        video.play();
    }
}

// 连接克隆人物视频
function connectCharacterVideo() {
    const characterVideo = document.getElementById('characterVideo');
    
    // 模拟克隆人物视频连接
    // 实际项目中，这里应该是从后端获取视频流或视频文件
    const video = document.createElement('video');
    video.autoplay = true;
    video.playsInline = true;
    
    // 使用示例视频URL或占位视频
    // 实际项目中应该替换为后端生成的视频流URL
    video.src = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4';
    video.loop = true;
    
    characterVideo.innerHTML = '';
    characterVideo.appendChild(video);
    
    characterVideoPlaying = true;
}

// 停止克隆人物视频
function stopCharacterVideo() {
    const characterVideo = document.getElementById('characterVideo');
    
    // 停止视频播放
    const video = characterVideo.querySelector('video');
    if (video) {
        video.pause();
        video.src = '';
        video.remove();
    }
    
    // 显示占位文本
    characterVideo.innerHTML = '<p>克隆人物视频已暂停</p>';
    
    characterVideoPlaying = false;
}

// 停止对话
function stopChat() {
    if (!chatActive) {
        showNotification('对话已经停止', 'info');
        return;
    }
    
    chatActive = false;
    
    // 停止用户视频和麦克风
    WebRTC.stopLocal();
    
    // 停止克隆人物视频
    stopCharacterVideo();
    
    // 重置用户视频显示
    const userVideo = document.getElementById('userVideo');
    userVideo.innerHTML = '<p>您的视频将显示在此</p>';
    
    // 更新按钮状态
    updateChatButton();
    
    showNotification('对话已停止', 'success');
}

// 切换对话状态（开始/停止）
function toggleChat() {
    if (chatActive) {
        stopChat();
    } else {
        startChat();
    }
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

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化聊天界面
    console.log('Chat page initialized');
});
