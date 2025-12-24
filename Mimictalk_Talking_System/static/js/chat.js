// 实时对话页面脚本

// 生成状态跟踪变量
let isGenerating = false;
let currentTaskId = null;
// 添加模拟进度变量
let simulateProgress = 0;
let simulateProgressInterval = null;

// 全局变量，用于存储上传的文件对象
let uploadedAudioFile = null;
let uploadedVideoFile = null;

// 页面加载时获取GPU信息和保存的模型目录
window.addEventListener('DOMContentLoaded', function() {
    loadGPUInfo();
    // 从localStorage获取保存的模型目录
    const savedModelDir = localStorage.getItem('modelDir');
    if (savedModelDir) {
        document.getElementById('modelDir').value = savedModelDir;
    }
    
    // 初始化聊天界面
    console.log('Chat page initialized');
    
    // 添加音频元素用于测试
    const audioElement = document.createElement('audio');
    audioElement.id = 'cloneAudio';
    audioElement.style.display = 'none';
    document.body.appendChild(audioElement);
    
    // 监听pitch控制变化
    const pitchControl = document.getElementById('pitchControl');
    const pitchValue = document.getElementById('pitchValue');
    if (pitchControl && pitchValue) {
        pitchControl.addEventListener('input', function() {
            pitchValue.textContent = this.value;
        });
    }
    
    // 监听speed控制变化
    const speedControl = document.getElementById('speedControl');
    const speedValue = document.getElementById('speedValue');
    if (speedControl && speedValue) {
        speedControl.addEventListener('input', function() {
            speedValue.textContent = this.value;
        });
    }
    
    // 初始化语音识别和语音按钮
    initVoiceRecognition();
    updateVoiceButtons();
    
    // 显示并启用语音控制按钮
    document.querySelector('.voice-controls').style.display = 'block';
    document.getElementById('voiceToggleBtn').disabled = false;
    
    // 进入页面时自动开启摄像头
    WebRTC.startLocalVideo('userVideo');
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

// 加载语音克隆模型列表
function loadVoiceCloneModels() {
    fetch('/api/voice-clone-models')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateVoiceCloneModelOptions(data.models);
            } else {
                console.error('获取语音克隆模型失败:', data.error);
                showNotification('获取语音克隆模型失败: ' + data.error, 'error');
                // 清空模型选项
                updateVoiceCloneModelOptions([]);
            }
        })
        .catch(error => {
            console.error('获取语音克隆模型出错:', error);
            showNotification('获取语音克隆模型出错: ' + error.message, 'error');
            // 清空模型选项
            updateVoiceCloneModelOptions([]);
        });
}

// 更新语音克隆模型选项
function updateVoiceCloneModelOptions(models) {
    const voiceCloneModelSelect = document.getElementById('voiceCloneModel');
    if (!voiceCloneModelSelect) return;
    
    // 清空现有选项
    voiceCloneModelSelect.innerHTML = '';
    
    // 添加新的模型选项
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.id;
        option.textContent = model.name;
        
        if (model.id === 'default_voice_clone') {
            option.selected = true;
        }
        
        voiceCloneModelSelect.appendChild(option);
    });
}

// 上传文件函数已在后面重新定义，这里不再需要

// 选择目录函数已在后面重新定义，这里不再需要

// 上传文件到服务器函数已在后面重新定义，这里不再需要

let recognition = null;
let isRecognizing = false;
let mediaRecorder = null;
let audioChunks = [];
let characterVideoPlaying = false;

// 当将来需要把 pitch 一并发给后端时，可使用此函数获取值
function getChatPitch() {
    const el = document.getElementById('pitchControl');
    return el ? parseInt(el.value) : 0;
}



// 初始化语音识别
function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'zh-CN';
        
        recognition.onstart = function() {
            isRecognizing = true;
            showNotification('正在聆听...', 'info');
            updateVoiceButtons();
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            addMessage(transcript, 'user');
            if (recognition && isRecognizing) {
                recognition.stop();
            }
            updateVoiceButtons();
            processUserMessage(transcript);
        };
        
        recognition.onerror = function(event) {
            console.error('语音识别错误:', event.error);
            showNotification('语音识别错误: ' + event.error, 'error');
            if (recognition && isRecognizing) {
                recognition.stop();
            }
            updateVoiceButtons();
        };
        
        recognition.onend = function() {
            isRecognizing = false;
            updateVoiceButtons();
        };
    } else {
        showNotification('您的浏览器不支持语音识别功能', 'error');
    }
}

// 切换语音识别状态
function toggleVoiceRecognition() {
    // 如果正在生成视频，执行停止生成操作
    if (isGenerating) {
        stopGeneration();
        return;
    }
    
    if (!recognition) {
        initVoiceRecognition();
    }
    
    if (isRecognizing) {
        recognition.stop();
    } else {
        recognition.start();
    }
}

// 更新语音按钮状态
function updateVoiceButtons() {
    const voiceBtn = document.getElementById('voiceToggleBtn');
    
    if (voiceBtn) {
        // 如果正在生成视频，显示停止生成按钮
        if (isGenerating) {
            voiceBtn.textContent = '停止生成';
            voiceBtn.className = 'btn-small btn-danger';
        } else if (isRecognizing) {
            voiceBtn.textContent = '录音中，点击结束';
            voiceBtn.className = 'btn-small btn-recording';
        } else {
            voiceBtn.textContent = '点击开始说话';
            voiceBtn.className = 'btn-small btn-primary';
        }
    }
}

// 更新生成状态的UI
function updateGenerationUI(isGenerating) {
    const characterVideo = document.getElementById('characterVideo');
    const voiceToggleBtn = document.getElementById('voiceToggleBtn');
    const chatForm = document.getElementById('chatForm');
    const generationButtons = chatForm.querySelectorAll('button');
    const generationInputs = chatForm.querySelectorAll('input, select, textarea');
    
    if (isGenerating) {
        // 创建进度条
        characterVideo.innerHTML = `
            <div class="generation-progress-container">
                <div class="generation-progress-bar">
                    <div class="generation-progress" style="width: 0%"></div>
                </div>
                <div class="generation-progress-text">视频生成中...</div>
            </div>
        `;
        
        // 禁用所有输入和按钮
        generationButtons.forEach(button => {
            if (button !== voiceToggleBtn) {
                button.disabled = true;
            }
        });
        
        generationInputs.forEach(input => {
            input.disabled = true;
        });
        
        // 更新语音按钮为停止生成
        updateVoiceButtons();
        
        // 重置模拟进度并开始模拟进度增长
        simulateProgress = 0;
        startSimulateProgress();
    } else {
        // 停止模拟进度增长
        stopSimulateProgress();
        
        // 只有在没有视频播放时才恢复原始视频容器内容
        if (!characterVideoPlaying) {
            characterVideo.innerHTML = '<p>克隆人物视频将显示在此（由后端生成）</p>';
        }
        
        // 启用所有输入和按钮
        generationButtons.forEach(button => {
            button.disabled = false;
        });
        
        generationInputs.forEach(input => {
            input.disabled = false;
        });
        
        // 更新语音按钮为正常状态
        updateVoiceButtons();
    }
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
        updateProgress(simulateProgress);
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
function updateProgress(progress) {
    const progressElement = document.querySelector('.generation-progress');
    const progressText = document.querySelector('.generation-progress-text');
    
    if (progressElement && progressText) {
        progress = Math.min(100, Math.max(0, progress));
        progressElement.style.width = progress + '%';
        progressText.textContent = `视频生成中... ${Math.round(progress)}%`;
    }
}

// 停止生成
function stopGeneration() {
    if (isGenerating && currentTaskId) {
        // 发送停止生成请求
        fetch(`/api/task/${currentTaskId}/stop`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('已停止视频生成', 'info');
            } else {
                showNotification('停止生成失败: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('停止生成请求错误:', error);
            showNotification('停止生成请求失败: ' + error.message, 'error');
        })
        .finally(() => {
            // 停止模拟进度增长
            stopSimulateProgress();
            
            // 恢复界面状态
            updateGenerationUI(false);
            isGenerating = false;
            currentTaskId = null;
        });
    }
}

// 处理用户消息
function processUserMessage(userMessage) {
    // 调用LLM生成回复
    generateLLMResponse(userMessage);
}

// 调用LLM生成回复
function generateLLMResponse(userMessage) {
    showNotification('正在生成回复...', 'info');
    
    // 调用后端LLM接口
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const botResponse = data.response;
            addMessage(botResponse, 'bot');
            
            // 生成语音和视频
            generateResponseAudioVideo(botResponse);
        } else {
            showNotification('生成回复失败: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('LLM API调用错误:', error);
        showNotification('LLM API调用失败: ' + error.message, 'error');
    });
}

// 生成回复的音频和视频
function generateResponseAudioVideo(botResponse) {
    // 设置生成状态为true
    isGenerating = true;
    
    // 更新界面状态
    updateGenerationUI(true);
    
    showNotification('正在生成语音和视频...', 'info');
    
    // 验证参考音频和视频是否存在
    console.log('检查上传的文件:', uploadedAudioFile, uploadedVideoFile);
    if (!uploadedAudioFile || !uploadedVideoFile) {
        showNotification('请先上传参考音频和视频', 'error');
        // 恢复界面状态
        updateGenerationUI(false);
        isGenerating = false;
        return;
    }
    
    // 获取模型目录和GPU选择
    const modelDir = document.getElementById('modelDir').value;
    const modelName = 'MimicTalk'; // 使用固定模型名，与generate.js一致
    const gpuSelect = document.getElementById('gpuSelect').value;
    const pitch = document.getElementById('pitchControl').value;
    const speed = document.getElementById('speedControl').value;
    
    // 保存模型目录地址
    localStorage.setItem('modelDir', modelDir);
    
    // 创建FormData
    const formData = new FormData();
    
    // 直接使用上传的文件对象
    formData.append('reference_audio', uploadedAudioFile);
    formData.append('reference_video', uploadedVideoFile);
    formData.append('model_name', modelName);
    formData.append('model_dir', modelDir);
    formData.append('gpu', gpuSelect);
    formData.append('target_text', botResponse);
    formData.append('pitch', pitch);
    formData.append('speed', speed);
    
    // 调试信息：显示上传的音频文件
    console.log('上传的参考音频文件:', uploadedAudioFile);
    
    // 调用现有的视频生成API，与generate.js使用相同的接口
    fetch('/api/generate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('视频生成已启动', 'success');
            // 保存当前任务ID
            currentTaskId = data.task_id;
            // 轮询任务状态获取视频URL
            pollTaskStatus(data.task_id);
        } else {
            showNotification('生成视频失败: ' + data.error, 'error');
            // 恢复界面状态
            updateGenerationUI(false);
            isGenerating = false;
            currentTaskId = null;
        }
    })
    .catch(error => {
        console.error('视频生成API调用错误:', error);
        showNotification('视频生成API调用失败: ' + error.message, 'error');
        // 恢复界面状态
        updateGenerationUI(false);
        isGenerating = false;
        currentTaskId = null;
    });
}

// 轮询任务状态
function pollTaskStatus(taskId) {
    const checkStatus = () => {
        fetch(`/api/task/${taskId}`)
            .then(response => response.json())
            .then(task => {
                if (task.status === 'completed') {
                    // 停止模拟进度增长
                    stopSimulateProgress();
                    
                    // 设置进度为100%
                    updateProgress(100);
                    
                    if (task.video_url) {
                        // 提取视频文件名
                        const videoFilename = task.video_url.split('/').pop();
                        playGeneratedVideo(videoFilename);
                    }
                    // 只更新状态变量，不立即恢复界面
                    isGenerating = false;
                    currentTaskId = null;
                } else if (task.status === 'failed') {
                    // 停止模拟进度增长
                    stopSimulateProgress();
                    
                    showNotification('视频生成失败', 'error');
                    // 恢复界面状态
                    updateGenerationUI(false);
                    isGenerating = false;
                    currentTaskId = null;
                } else {
                    // 继续轮询
                    setTimeout(checkStatus, 1000);
                }
            })
            .catch(error => {
                console.error('获取任务状态失败:', error);
                showNotification('获取任务状态失败: ' + error.message, 'error');
            });
    };
    
    // 开始轮询
    checkStatus();
}

// 播放生成的视频
function playGeneratedVideo(videoFilename) {
    const characterVideo = document.getElementById('characterVideo');
    
    // 创建新的视频元素
    const video = document.createElement('video');
    video.autoplay = true;
    video.playsInline = true;
    video.muted = true; // 添加静音属性确保自动播放
    video.src = `/static/videos/${videoFilename}`;
    
    // 监听视频加载事件
    video.onloadeddata = function() {
        console.log('视频加载完成');
        showNotification('视频加载完成', 'success');
    };
    
    // 监听视频播放事件，取消静音
    video.onplay = function() {
        setTimeout(() => {
            video.muted = false;
        }, 100);
        console.log('视频开始播放');
    };
    
    // 监听视频播放结束事件
    video.onended = function() {
        characterVideoPlaying = false;
        console.log('视频播放结束');
        // 恢复界面状态
        updateGenerationUI(false);
        isGenerating = false;
        currentTaskId = null;
    };
    
    // 监听视频错误事件
    video.onerror = function(error) {
        console.error('视频播放错误:', error);
        showNotification('视频播放失败', 'error');
        // 恢复界面状态
        updateGenerationUI(false);
        isGenerating = false;
        currentTaskId = null;
    };
    
    // 清空容器并添加新视频
    characterVideo.innerHTML = '';
    characterVideo.appendChild(video);
    
    characterVideoPlaying = true;
    showNotification('视频播放开始', 'success');
    console.log('视频URL:', video.src);
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





// 上传文件
function uploadFile(type) {
    const input = document.createElement('input');
    input.type = 'file';
    
    if (type === 'video') {
        input.accept = 'video/*';
    } else if (type === 'audio') {
        input.accept = 'audio/*';
    } else if (type === 'image') {
        input.accept = 'image/*';
    }
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (type === 'audio') {
                uploadedAudioFile = file;
                // 将文件上传到服务器并获取URL
                const formData = new FormData();
                formData.append('file', file);
                
                fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // 保存上传的文件对象
                        uploadedAudioFile = file;
                        // 将文件名显示在输入框中
                        document.getElementById('referenceAudio').value = file.name;
                        showNotification('音频文件上传成功', 'success');
                    } else {
                        showNotification('音频文件上传失败: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    console.error('文件上传出错:', error);
                    showNotification('文件上传出错: ' + error.message, 'error');
                });
            } else if (type === 'video') {
                uploadedVideoFile = file;
                // 将文件上传到服务器并获取URL
                const formData = new FormData();
                formData.append('file', file);
                
                fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // 保存上传的文件对象
                        uploadedVideoFile = file;
                        // 将文件名显示在输入框中
                        document.getElementById('referenceVideo').value = file.name;
                        showNotification('视频文件上传成功', 'success');
                    } else {
                        showNotification('视频文件上传失败: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    console.error('文件上传出错:', error);
                    showNotification('文件上传出错: ' + error.message, 'error');
                });
            }
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