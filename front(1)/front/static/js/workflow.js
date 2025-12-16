// 一条龙体验流程控制

// 全局变量
let currentStep = 1;
const totalSteps = 5;
let workflowParams = {};
let guideStep = 0;

// 引导步骤配置
const guideSteps = [
    {
        title: "欢迎使用一条龙体验",
        description: "这是一个引导您完成从模型训练到实时对话的全流程助手。让我们开始吧！",
        target: null
    },
    {
        title: "选择核心模型",
        description: "请选择您想要使用的核心模型，不同模型有不同的特点和效果。",
        target: "#coreModel"
    },
    {
        title: "上传参考视频",
        description: "请上传包含清晰人脸的参考视频，这是训练模型的基础素材。",
        target: "#referenceVideo"
    },
    {
        title: "开始训练",
        description: "配置好参数后，点击下一步开始模型训练。",
        target: "#nextBtn"
    }
];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeWorkflow();
});

// 初始化工作流
function initializeWorkflow() {
    // 设置事件监听器
    setupEventListeners();
    
    // 加载保存的参数（如果有）
    loadWorkflowParams();
    
    // 显示当前步骤
    showStep(currentStep);
}

// 设置事件监听器
function setupEventListeners() {
    // 对话API选择变化
    document.getElementById('chatApi').addEventListener('change', function() {
        toggleApiKeySection();
    });
    
    // 温度滑块变化
    document.getElementById('temperature').addEventListener('input', function() {
        document.getElementById('temperatureValue').textContent = this.value;
    });
    
    // 升降调滑块变化
    document.getElementById('pitchControl').addEventListener('input', function() {
        document.getElementById('pitchValue').textContent = this.value;
    });
}

// 显示指定步骤
function showStep(step) {
    // 更新当前步骤
    currentStep = step;
    
    // 隐藏所有步骤
    const steps = document.querySelectorAll('.workflow-step');
    steps.forEach(s => s.classList.remove('active'));
    
    // 显示当前步骤
    const currentStepElement = document.getElementById('step' + step);
    if (currentStepElement) {
        currentStepElement.classList.add('active');
    }
    
    // 更新进度条
    updateProgressBar(step);
    
    // 更新步骤说明
    updateStepInstructions(step);
    
    // 更新操作按钮
    updateActionButtons(step);
    
    // 如果是最后一步，显示完成按钮
    if (step === totalSteps) {
        document.getElementById('finishBtn').style.display = 'block';
        document.getElementById('nextBtn').style.display = 'none';
    } else {
        document.getElementById('finishBtn').style.display = 'none';
        document.getElementById('nextBtn').style.display = 'inline-block';
    }
}

// 更新进度条
function updateProgressBar(step) {
    // 更新步骤状态
    const progressSteps = document.querySelectorAll('.progress-step');
    const progressLines = document.querySelectorAll('.progress-line');
    
    progressSteps.forEach((progressStep, index) => {
        if (index < step) {
            progressStep.classList.add('active');
        } else {
            progressStep.classList.remove('active');
        }
    });
    
    progressLines.forEach((progressLine, index) => {
        if (index < step - 1) {
            progressLine.classList.add('active');
        } else {
            progressLine.classList.remove('active');
        }
    });
}

// 更新步骤说明
function updateStepInstructions(step) {
    const stepTitles = [
        "基础配置",
        "模型训练",
        "视频生成",
        "对话配置",
        "实时对话"
    ];
    
    // 将步骤说明和提示文本分开定义
    const stepContent = [
        {
            description: "欢迎使用一条龙体验流程！在这一步，您需要选择核心模型、GPU配置和上传参考视频。",
            tip: "参考视频需包含清晰的人脸，时长建议5-30秒。"
        },
        {
            description: "现在您可以配置模型训练的参数，包括训练轮数和自定义参数。",
            tip: "训练时间取决于视频时长和GPU性能。"
        },
        {
            description: "在这一步，您需要配置视频生成的参数，包括参考音频、语音克隆模型等。",
            tip: "您可以上传音频或输入文字来生成语音。"
        },
        {
            description: "现在您可以配置实时对话的参数，包括对话API和高级参数。",
            tip: "Local LLM无需配置API密钥，OpenAI/Claude需要。"
        },
        {
            description: "恭喜！您已完成所有配置，可以开始与克隆人物进行实时对话了。",
            tip: "在左侧输入消息，克隆人物将以视频形式回复您。"
        }
    ];
    
    document.getElementById('currentStepNumber').textContent = step;
    document.getElementById('currentStepTitle').textContent = stepTitles[step - 1];
    
    // 将提示文本包装在特定的HTML标签中
    const currentContent = stepContent[step - 1];
    document.getElementById('stepDescription').innerHTML = `
        ${currentContent.description}<br>
        <span class="step-tip">提示：${currentContent.tip}</span>
    `;
}

// 更新操作按钮
function updateActionButtons(step) {
    // 上一步按钮
    const prevBtn = document.getElementById('prevBtn');
    if (step === 1) {
        prevBtn.disabled = true;
    } else {
        prevBtn.disabled = false;
    }
    
    // 下一步按钮文本
    const nextBtn = document.getElementById('nextBtn');
    if (step === totalSteps - 1) {
        nextBtn.textContent = '进入对话';
    } else {
        nextBtn.textContent = '下一步';
    }
    
    // 跳过按钮
    const skipBtn = document.getElementById('skipBtn');
    if (step === totalSteps) {
        skipBtn.style.display = 'none';
    } else {
        skipBtn.style.display = 'inline-block';
    }
}

// 下一步
function goToNextStep() {
    // 验证当前步骤
    if (!validateCurrentStep()) {
        return;
    }
    
    // 保存当前步骤参数
    saveCurrentStepParams();
    
    // 处理特殊步骤
    if (currentStep === 2) {
        // 开始训练
        startTraining();
        return;
    } else if (currentStep === 3) {
        // 开始生成视频
        generateVideo();
        return;
    } else if (currentStep === 4) {
        // 进入对话
        enterChat();
        return;
    }
    
    // 进入下一步
    if (currentStep < totalSteps) {
        showStep(currentStep + 1);
    }
}

// 上一步
function goToPreviousStep() {
    if (currentStep > 1) {
        showStep(currentStep - 1);
    }
}

// 跳过当前步骤
function skipCurrentStep() {
    // 保存当前步骤的默认参数
    saveDefaultStepParams();
    
    // 进入下一步
    if (currentStep < totalSteps) {
        showStep(currentStep + 1);
    }
}

// 完成工作流
function finishWorkflow() {
    // 保存最后一步参数
    saveCurrentStepParams();
    
    // 保存所有参数
    saveWorkflowParams();
    
    // 跳转到聊天页面
    window.location.href = '/chat';
}

// 验证当前步骤
function validateCurrentStep() {
    let isValid = true;
    
    switch (currentStep) {
        case 1:
            // 验证基础配置
            isValid = validateBasicConfig();
            break;
        case 2:
            // 验证训练配置
            isValid = validateTrainConfig();
            break;
        case 3:
            // 验证生成配置
            isValid = validateGenerateConfig();
            break;
        case 4:
            // 验证对话配置
            isValid = validateChatConfig();
            break;
    }
    
    return isValid;
}

// 验证基础配置
function validateBasicConfig() {
    const referenceVideo = document.getElementById('referenceVideo').value;
    
    if (!referenceVideo) {
        alert('请上传或输入参考视频路径');
        return false;
    }
    
    return true;
}

// 验证训练配置
function validateTrainConfig() {
    // 训练配置总是有效的，使用默认值
    return true;
}

// 验证生成配置
function validateGenerateConfig() {
    const referenceAudio = document.getElementById('referenceAudio').value;
    const targetText = document.getElementById('targetText').value;
    
    if (!referenceAudio && !targetText) {
        alert('请上传参考音频或输入目标文字');
        return false;
    }
    
    return true;
}

// 验证对话配置
function validateChatConfig() {
    const chatApi = document.getElementById('chatApi').value;
    const apiKey = document.getElementById('apiKey').value;
    
    if ((chatApi === 'OpenAI API' || chatApi === 'Claude API') && !apiKey) {
        alert('请输入API密钥');
        return false;
    }
    
    return true;
}

// 保存当前步骤参数
function saveCurrentStepParams() {
    switch (currentStep) {
        case 1:
            saveBasicConfig();
            break;
        case 2:
            saveTrainConfig();
            break;
        case 3:
            saveGenerateConfig();
            break;
        case 4:
            saveChatConfig();
            break;
    }
    
    // 保存到localStorage
    saveWorkflowParams();
}

// 保存默认步骤参数
function saveDefaultStepParams() {
    switch (currentStep) {
        case 1:
            workflowParams.basicConfig = {
                coreModel: 'SyncTalk',
                gpuSelect: 'GPU0',
                referenceVideo: ''
            };
            break;
        case 2:
            workflowParams.trainConfig = {
                trainingEpochs: 50,
                customTrainingParams: {}
            };
            break;
        case 3:
            workflowParams.generateConfig = {
                referenceAudio: '',
                voiceCloneModel: 'Voice Clone A',
                pitchControl: 0,
                targetText: '',
                tfgRemoveBg: false
            };
            break;
        case 4:
            workflowParams.chatConfig = {
                chatApi: 'Local LLM',
                apiKey: '',
                temperature: 0.7,
                maxResponseLength: 500
            };
            break;
    }
    
    // 保存到localStorage
    saveWorkflowParams();
}

// 保存基础配置
function saveBasicConfig() {
    workflowParams.basicConfig = {
        coreModel: document.getElementById('coreModel').value,
        gpuSelect: document.getElementById('gpuSelect').value,
        referenceVideo: document.getElementById('referenceVideo').value
    };
}

// 保存训练配置
function saveTrainConfig() {
    workflowParams.trainConfig = {
        trainingEpochs: parseInt(document.getElementById('trainingEpochs').value),
        customTrainingParams: parseCustomParams(document.getElementById('customTrainingParams').value)
    };
}

// 保存生成配置
function saveGenerateConfig() {
    workflowParams.generateConfig = {
        referenceAudio: document.getElementById('referenceAudio').value,
        voiceCloneModel: document.getElementById('voiceCloneModel').value,
        pitchControl: parseInt(document.getElementById('pitchControl').value),
        targetText: document.getElementById('targetText').value,
        tfgRemoveBg: document.getElementById('tfgRemoveBg').checked
    };
}

// 保存对话配置
function saveChatConfig() {
    workflowParams.chatConfig = {
        chatApi: document.getElementById('chatApi').value,
        apiKey: document.getElementById('apiKey').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        maxResponseLength: parseInt(document.getElementById('maxResponseLength').value)
    };
}

// 解析自定义参数
function parseCustomParams(paramsText) {
    if (!paramsText) return {};
    
    try {
        return JSON.parse(paramsText);
    } catch (e) {
        alert('自定义参数格式错误，请使用JSON格式');
        return {};
    }
}

// 加载工作流参数
function loadWorkflowParams() {
    const savedParams = localStorage.getItem('workflowParams');
    if (savedParams) {
        workflowParams = JSON.parse(savedParams);
        
        // 加载到表单
        loadBasicConfig();
        loadTrainConfig();
        loadGenerateConfig();
        loadChatConfig();
    }
}

// 保存工作流参数到localStorage
function saveWorkflowParams() {
    localStorage.setItem('workflowParams', JSON.stringify(workflowParams));
}

// 加载基础配置到表单
function loadBasicConfig() {
    if (workflowParams.basicConfig) {
        document.getElementById('coreModel').value = workflowParams.basicConfig.coreModel || 'SyncTalk';
        document.getElementById('gpuSelect').value = workflowParams.basicConfig.gpuSelect || 'GPU0';
        document.getElementById('referenceVideo').value = workflowParams.basicConfig.referenceVideo || '';
    }
}

// 加载训练配置到表单
function loadTrainConfig() {
    if (workflowParams.trainConfig) {
        document.getElementById('trainingEpochs').value = workflowParams.trainConfig.trainingEpochs || 50;
        document.getElementById('customTrainingParams').value = JSON.stringify(workflowParams.trainConfig.customTrainingParams || {}, null, 2);
    }
}

// 加载生成配置到表单
function loadGenerateConfig() {
    if (workflowParams.generateConfig) {
        document.getElementById('referenceAudio').value = workflowParams.generateConfig.referenceAudio || '';
        document.getElementById('voiceCloneModel').value = workflowParams.generateConfig.voiceCloneModel || 'Voice Clone A';
        document.getElementById('pitchControl').value = workflowParams.generateConfig.pitchControl || 0;
        document.getElementById('targetText').value = workflowParams.generateConfig.targetText || '';
        document.getElementById('tfgRemoveBg').checked = workflowParams.generateConfig.tfgRemoveBg || false;
        
        // 更新显示值
        document.getElementById('pitchValue').textContent = workflowParams.generateConfig.pitchControl || 0;
    }
}

// 加载对话配置到表单
function loadChatConfig() {
    if (workflowParams.chatConfig) {
        document.getElementById('chatApi').value = workflowParams.chatConfig.chatApi || 'Local LLM';
        document.getElementById('apiKey').value = workflowParams.chatConfig.apiKey || '';
        document.getElementById('temperature').value = workflowParams.chatConfig.temperature || 0.7;
        document.getElementById('maxResponseLength').value = workflowParams.chatConfig.maxResponseLength || 500;
        
        // 更新显示值
        document.getElementById('temperatureValue').textContent = workflowParams.chatConfig.temperature || 0.7;
        
        // 显示/隐藏API密钥区域
        toggleApiKeySection();
    }
}

// 切换API密钥区域
function toggleApiKeySection() {
    const chatApi = document.getElementById('chatApi').value;
    const apiKeySection = document.getElementById('apiKeySection');
    
    if (chatApi === 'OpenAI API' || chatApi === 'Claude API') {
        apiKeySection.style.display = 'flex';
    } else {
        apiKeySection.style.display = 'none';
    }
}

// 切换自定义训练参数
function toggleCustomParams() {
    const customParamsSection = document.getElementById('customParamsSection');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (customParamsSection.style.display === 'none') {
        customParamsSection.style.display = 'block';
        toggleIcon.textContent = '▲';
    } else {
        customParamsSection.style.display = 'none';
        toggleIcon.textContent = '▼';
    }
}

// 切换聊天参数
function toggleChatParams() {
    const chatParamsSection = document.getElementById('chatParamsSection');
    const chatToggleIcon = document.getElementById('chatToggleIcon');
    
    if (chatParamsSection.style.display === 'none') {
        chatParamsSection.style.display = 'block';
        chatToggleIcon.textContent = '▲';
    } else {
        chatParamsSection.style.display = 'none';
        chatToggleIcon.textContent = '▼';
    }
}

// 开始训练
function startTraining() {
    // 显示进度条
    showProgressBar();
    
    // 模拟训练进度
    let progress = 0;
    const interval = setInterval(function() {
        progress += 5;
        updateProgress(progress);
        
        if (progress >= 100) {
            clearInterval(interval);
            
            // 训练完成，进入下一步
            setTimeout(function() {
                hideProgressBar();
                showStep(3);
            }, 1000);
        }
    }, 300);
}

// 生成视频
function generateVideo() {
    // 显示进度条
    showProgressBar();
    
    // 模拟生成进度
    let progress = 0;
    const interval = setInterval(function() {
        progress += 4;
        updateProgress(progress);
        
        if (progress >= 100) {
            clearInterval(interval);
            
            // 生成完成，进入下一步
            setTimeout(function() {
                hideProgressBar();
                showStep(4);
            }, 1000);
        }
    }, 300);
}

// 进入对话
function enterChat() {
    // 保存最后一步参数
    saveCurrentStepParams();
    
    // 跳转到对话页面
    window.location.href = '/chat';
}

// 显示进度条
function showProgressBar() {
    const progressBar = document.getElementById('taskProgress');
    progressBar.style.display = 'block';
}

// 隐藏进度条
function hideProgressBar() {
    const progressBar = document.getElementById('taskProgress');
    progressBar.style.display = 'none';
}

// 更新进度
function updateProgress(percent) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    progressFill.style.width = percent + '%';
    progressText.textContent = percent + '%';
    
    // 更新预计时间
    updateEstimatedTime(percent);
}

// 更新预计时间
function updateEstimatedTime(percent) {
    if (percent === 0) {
        document.getElementById('estimatedTime').textContent = '预计剩余时间：计算中...';
        return;
    }
    
    const totalTime = currentStep === 2 ? 600 : 300; // 训练600秒，生300秒
    const elapsedTime = (percent / 100) * totalTime;
    const remainingTime = totalTime - elapsedTime;
    
    const minutes = Math.floor(remainingTime / 60);
    const seconds = Math.floor(remainingTime % 60);
    
    document.getElementById('estimatedTime').textContent = `预计剩余时间：${minutes}分${seconds}秒`;
}

// 上传文件
function uploadFile(type) {
    // 创建文件输入
    const input = document.createElement('input');
    input.type = 'file';
    
    if (type === 'video') {
        input.accept = 'video/mp4,video/mov,video/webm';
    } else if (type === 'audio') {
        input.accept = 'audio/*';
    }
    
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            // 模拟上传
            uploadFileToServer(file, type);
        }
    };
    
    input.click();
}

// 模拟文件上传到服务器
function uploadFileToServer(file, type) {
    // 显示上传进度
    showProgressBar();
    
    // 模拟上传进度
    let progress = 0;
    const interval = setInterval(function() {
        progress += 10;
        updateProgress(progress);
        
        if (progress >= 100) {
            clearInterval(interval);
            
            // 上传完成
            setTimeout(function() {
                hideProgressBar();
                
                // 更新文件路径
                const filePath = `/uploads/${file.name}`;
                if (type === 'video') {
                    document.getElementById('referenceVideo').value = filePath;
                    showVideoPreview(filePath);
                } else if (type === 'audio') {
                    document.getElementById('referenceAudio').value = filePath;
                }
            }, 500);
        }
    }, 200);
}

// 显示视频预览
function showVideoPreview(videoPath) {
    const previewContent = document.getElementById('previewContent');
    previewContent.innerHTML = `<video controls src="${videoPath}"></video>`;
}

// 选择目录
function selectDirectory() {
    // 模拟选择目录
    const directoryPath = '/models/custom_model';
    document.getElementById('modelDir').value = directoryPath;
}

// 开始新手引导
function startGuide() {
    guideStep = 0;
    showGuide();
}

// 显示引导
function showGuide() {
    const overlay = document.getElementById('guideOverlay');
    const content = document.getElementById('guideContent');
    const title = document.getElementById('guideTitle');
    const description = document.getElementById('guideDescription');
    
    if (guideStep >= 0 && guideStep < guideSteps.length) {
        const step = guideSteps[guideStep];
        
        title.textContent = step.title;
        description.textContent = step.description;
        
        // 高亮目标元素
        highlightTarget(step.target);
        
        overlay.style.display = 'flex';
    } else {
        closeGuide();
    }
}

// 上一个引导步骤
function previousGuide() {
    if (guideStep > 0) {
        guideStep--;
        showGuide();
    }
}

// 下一个引导步骤
function nextGuide() {
    if (guideStep < guideSteps.length - 1) {
        guideStep++;
        showGuide();
    } else {
        closeGuide();
    }
}

// 关闭引导
function closeGuide() {
    const overlay = document.getElementById('guideOverlay');
    overlay.style.display = 'none';
    
    // 移除所有高亮
    removeAllHighlights();
}

// 高亮目标元素
function highlightTarget(targetSelector) {
    removeAllHighlights();
    
    if (targetSelector) {
        const target = document.querySelector(targetSelector);
        if (target) {
            target.style.outline = '3px solid #ff6b6b';
            target.style.boxShadow = '0 0 20px rgba(255, 107, 107, 0.5)';
        }
    }
}

// 移除所有高亮
function removeAllHighlights() {
    const elements = document.querySelectorAll('*');
    elements.forEach(el => {
        el.style.outline = '';
        el.style.boxShadow = '';
    });
}

// 键盘事件处理
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// 发送消息
function sendMessage() {
    const messageInput = document.getElementById('userMessage');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // 清空输入
    messageInput.value = '';
    
    // 添加到对话历史
    addMessageToHistory('user', message);
    
    // 模拟回复
    setTimeout(() => {
        addMessageToHistory('bot', '这是对您消息的回复：' + message);
    }, 1000);
}

// 添加消息到历史
function addMessageToHistory(sender, message) {
    const chatMessages = document.querySelector('.chat-messages');
    
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message ' + sender;
    messageElement.innerHTML = `<div class="message-content">${message}</div>`;
    
    chatMessages.appendChild(messageElement);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}