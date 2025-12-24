const UI = (function(){
    function setTheme(theme){
        localStorage.setItem('selectedTheme', theme);

        const navbar = document.querySelector('.navbar');
        const navText = document.querySelectorAll('.nav-brand, .nav-menu a, .btn-small'); // 导航文字元素
        const root = document.documentElement;
        
        let navBg = '';
        let textColor = '#000000'; // 默认黑
        let bgGradient = '';
        let accent1 = '';
        let accent2 = '';
        let muted = '';
        let cardBg = '';
        let primaryBlue = '';
        let primaryPurple = '';
        let primaryPink = '';

        switch(theme){
            case 'elegant-gray':
                navBg = 'linear-gradient(135deg, #a9a9a9 0%, #808080 100%)';
                bgGradient = 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)';
                accent1 = '#808080';
                accent2 = '#a9a9a9';
                muted = '#666666';
                cardBg = '#ffffff';
                primaryBlue = 'linear-gradient(135deg, #808080 0%, #666666 100%)';
                primaryPurple = 'linear-gradient(135deg, #cccccc 0%, #b3b3b3 100%)';
                primaryPink = 'linear-gradient(135deg, #e0e0e0 0%, #d3d3d3 100%)';
                break;
            case 'light-green':
                navBg = 'linear-gradient(135deg, #98fb98 0%, #90ee90 100%)';
                textColor = '#111'; // 深色文本在浅色背景上清晰可见
                bgGradient = 'linear-gradient(135deg, #f0fff4 0%, #e6ffe6 100%)';
                accent1 = '#22c55e';
                accent2 = '#16a34a';
                muted = '#6b7280';
                cardBg = '#ffffff';
                primaryBlue = 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)';
                primaryPurple = 'linear-gradient(135deg, #bbf7d0 0%, #86efac 100%)';
                primaryPink = 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)';
                break;
            case 'summer-yellow':
                navBg = 'linear-gradient(135deg, #ffd700 0%, #ffc107 100%)';
                textColor = '#111'; // 深色文本在浅色背景上清晰可见
                bgGradient = 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)';
                accent1 = '#f59e0b';
                accent2 = '#d97706';
                muted = '#6b7280';
                cardBg = '#ffffff';
                primaryBlue = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
                primaryPurple = 'linear-gradient(135deg, #fde68a 0%, #fbbf24 100%)';
                primaryPink = 'linear-gradient(135deg, #fef08a 0%, #fde68a 100%)';
                break;
            case 'peach-pink':
                navBg = 'linear-gradient(135deg, #ffb6c1 0%, #ff69b4 100%)';
                textColor = '#111'; // 深色文本在浅色背景上清晰可见
                bgGradient = 'linear-gradient(135deg, #fff1f2 0%, #fecdd3 100%)';
                accent1 = '#ec4899';
                accent2 = '#db2777';
                muted = '#6b7280';
                cardBg = '#ffffff';
                primaryBlue = 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)';
                primaryPurple = 'linear-gradient(135deg, #fbcfe8 0%, #f9a8d4 100%)';
                primaryPink = 'linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%)';
                break;
            case 'star-purple':
                navBg = 'linear-gradient(135deg, #9370db 0%, #8a2be2 100%)';
                textColor = '#111'; // 深色文本在浅色背景上清晰可见
                bgGradient = 'linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%)';
                accent1 = '#8b5cf6';
                accent2 = '#7c3aed';
                muted = '#6b7280';
                cardBg = '#ffffff';
                primaryBlue = 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)';
                primaryPurple = 'linear-gradient(135deg, #d8b4fe 0%, #c084fc 100%)';
                primaryPink = 'linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%)';
                break;
            case 'classic-blue':
                navBg = 'linear-gradient(135deg, #6495ed 0%, #4169e1 100%)';
                textColor = '#111'; // 深色文本在浅色背景上清晰可见
                bgGradient = 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)';
                accent1 = '#3b82f6';
                accent2 = '#2563eb';
                muted = '#6b7280';
                cardBg = '#ffffff';
                primaryBlue = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
                primaryPurple = 'linear-gradient(135deg, #bfdbfe 0%, #93c5fd 100%)';
                primaryPink = 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)';
                break;
            case 'vital-red':
                navBg = 'linear-gradient(135deg, #ff6347 0%, #ff4500 100%)';
                textColor = '#111'; // 深色文本在浅色背景上清晰可见
                bgGradient = 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)';
                accent1 = '#ef4444';
                accent2 = '#dc2626';
                muted = '#6b7280';
                cardBg = '#ffffff';
                primaryBlue = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
                primaryPurple = 'linear-gradient(135deg, #fca5a5 0%, #f87171 100%)';
                primaryPink = 'linear-gradient(135deg, #fecaca 0%, #fca5a5 100%)';
                break;
            case 'ultimate-black':
                navBg = 'linear-gradient(135deg, #333333 0%, #111111 100%)';
                textColor = '#ffffff'; // 深色主题文字颜色为白色
                bgGradient = 'linear-gradient(135deg, #1f2937 0%, #111827 100%)';
                accent1 = '#6b7280';
                accent2 = '#4b5563';
                muted = '#9ca3af';
                cardBg = '#374151';
                primaryBlue = 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)';
                primaryPurple = 'linear-gradient(135deg, #374151 0%, #1f2937 100%)';
                primaryPink = 'linear-gradient(135deg, #4b5563 0%, #374151 100%)';
                break;
            case 'minimal-white':
            default:
                navBg = 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)';
                bgGradient = 'linear-gradient(135deg, #eef2ff 0%, #e6f0ff 100%)';
                accent1 = '#6c63ff';
                accent2 = '#8b6bff';
                muted = '#6b7280';
                cardBg = '#ffffff';
                primaryBlue = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                primaryPurple = 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)';
                primaryPink = 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)';
                break;
        }

        // 更新导航栏样式
        if(navbar) navbar.style.background = navBg;
        
        // 根据导航栏背景设置合适的导航文本颜色
        const darkThemes = ['elegant-gray', 'ultimate-black', 'light-green', 'peach-pink', 'star-purple', 'classic-blue', 'vital-red'];
        const navTextColor = darkThemes.includes(theme) ? '#ffffff' : '#111';
        navText.forEach(el => el.style.color = navTextColor);
        
        // 更新CSS变量
        root.style.setProperty('--bg-gradient', bgGradient);
        root.style.setProperty('--accent-1', accent1);
        root.style.setProperty('--accent-2', accent2);
        root.style.setProperty('--muted', muted);
        root.style.setProperty('--card-bg', cardBg);
        root.style.setProperty('--text-color', textColor);
        root.style.setProperty('--primary-blue', primaryBlue);
        root.style.setProperty('--primary-purple', primaryPurple);
        root.style.setProperty('--primary-pink', primaryPink);
        
        // 更新所有文字颜色
        document.querySelectorAll('body, h1, h2, h3, h4, h5, h6, p, div, span').forEach(el => {
            el.style.color = textColor;
        });
    }

    // 加载保存的主题
    function loadSavedTheme(){
        const saved = localStorage.getItem('selectedTheme') || 'minimal-white';
        UI.setTheme(saved);
        const select = document.getElementById('themeSelect');
        if(select) select.value = saved;
    }
    function setFont(font){
        let fontFamily = '';
        switch(font){
            case 'serif':
                fontFamily = 'Georgia, serif';
                break;
            case 'sans-serif':
                fontFamily = 'Arial, sans-serif';
                break;
            case 'monospace':
                fontFamily = 'Courier New, monospace';
                break;
            case 'cursive':
                fontFamily = 'Comic Sans MS, cursive';
                break;
            default:
                fontFamily = "'Inter', 'Microsoft YaHei', Arial, sans-serif";
                break;
        }
        console.log('Setting font to: ' + fontFamily); // 诊断日志
        document.documentElement.style.setProperty('--font-family', fontFamily);
        applyFontToAll(fontFamily); // 调用新函数
        localStorage.setItem('selectedFont', font);
    }

    function applyFontToAll(fontFamily) {
        const allElements = document.querySelectorAll('*');
        allElements.forEach(el => {
            el.style.fontFamily = fontFamily;
        });
    }

    // 加载保存字体
    function loadSavedFont(){
        const saved = localStorage.getItem('selectedFont') || 'default';
        setFont(saved);
        const select = document.getElementById('fontSelect');
        if(select) select.value = saved;
    }

    // 定义不同页面的引导步骤
    const tourStepsTrain = [
        {sel: '.nav-brand', text: '欢迎使用系统！这是导航栏标题，点击可返回首页。系统主要用于训练语音模型、生成视频和实时对话。'},
        {sel: '.left-panel .video-container', text: '左侧面板显示训练视频或结果。训练完成后，这里会展示生成的视频预览。'},
        {sel: '.right-panel .form-container', text: '右侧面板用于设置训练参数，包括模型选择、视频上传等。填写后点击开始训练。'},
        {sel: '.btn-train', text: '点击这个按钮启动模型训练。训练需要时间，进度条会显示进度。注意选择合适的GPU和Epoch以避免过长等待。'},
        {sel: '#modelName', text: '这里选择模型，如SyncTalk，用于唇音同步训练。'},
        {sel: '#referenceVideo', text: '上传或输入参考视频，这是训练的核心数据。确保视频清晰。'},
        {sel: '#gpuSelect', text: '选择GPU加速训练。如果有多个GPU可用，选择空闲的。'},
        {sel: '#epochs', text: '设置训练轮数。初次测试用小值如10，避免资源浪费。'}
    ];

    const tourStepsGenerate = [
        {sel: '.nav-brand', text: '这是视频生成页面。系统使用训练好的模型生成唇音同步视频。'},
        {sel: '.left-panel .video-container', text: '左侧显示生成的视频。生成后可直接播放和下载。'},
        {sel: '.right-panel .form-container', text: '右侧设置生成参数，如模型目录、音频和文本。'},
        {sel: '.btn-generate', text: '点击生成视频。过程包括语音合成和视频渲染，需耐心等待。'},
        {sel: '#modelDir', text: '输入训练好的模型目录路径。这是生成的基础。'},
        {sel: '#referenceAudio', text: '上传参考音频，用于语音克隆。'},
        {sel: '#targetText', text: '输入目标文字，系统会合成语音并同步到视频。'},
        {sel: '#pitchControl', text: '调整音频音调，正值升调，负值降调。'}
    ];

    const tourStepsChat = [
        {sel: '.nav-brand', text: '实时对话页面，用于与克隆人物互动。系统结合语音识别和合成实现对话。'},
        {sel: '.chat-container', text: '左侧上部是克隆人物视频，下部是您的摄像头视频。用于实时视频对话。'},
        {sel: '.right-panel .form-container', text: '右侧配置对话参数，如模型和API选择。'},
        /*{sel: '#characterVideo', text: '这里显示克隆人物的视频响应。系统会根据您的输入生成同步视频。'},
        /*{sel: '#userVideo', text: '您的摄像头视频。系统通过麦克风和摄像头捕获输入，实现面对面对话。'},*/
        {sel: '#apiSelect', text: '选择对话API，如OpenAI，用于处理自然语言。'},
        {sel: '.btn-stop', text: '点击停止当前对话，重置界面。'}
    ];

    const tourStepsWorkflow = [
        {sel: '.nav-brand', text: '欢迎使用一条龙体验流程！这是导航栏标题，点击可返回首页。'},
        {sel: '.workflow-progress', text: '这是流程进度条，显示当前所处的步骤。总共包含5个步骤，从基础配置到实时对话。'},
        {sel: '.left-panel.workflow-info', text: '当前面板包含三个主要部分：当前步骤说明、任务进度显示和文件预览区域。'},
        {sel: '#stepDescription', text: '这里会显示当前步骤的详细说明和提示信息，帮助您了解每个步骤的操作要点。'},
        {sel: '#previewArea', text: '选择或上传文件后，预览内容会显示在这里，让您直观查看文件内容。'},
        {sel: '.right-panel.workflow-forms', text: '该面板用于配置各步骤的参数，当前显示的是基础配置页面。'},
        {sel: '#coreModel', text: '选择核心模型，如SyncTalk、Wav2Lip或MoFA-Talk，这是整个流程的基础。'},
        {sel: '#referenceVideo', text: '输入参考视频路径或上传视频文件，用于模型训练。视频需要包含清晰的人脸，时长建议5-30秒。'},
        {sel: '.workflow-actions', text: '底部的操作按钮用于导航到上一步、下一步或跳过当前步骤，完成整个工作流程。'}
    ];

    // 根据页面选择steps
    let tourSteps = [];
    if (window.location.pathname.includes('/train')) {
        tourSteps = tourStepsTrain;
    } else if (window.location.pathname.includes('/generate')) {
        tourSteps = tourStepsGenerate;
    } else if (window.location.pathname.includes('/chat')) {
        tourSteps = tourStepsChat;
    } else if (window.location.pathname.includes('/workflow')) {
        tourSteps = tourStepsWorkflow;
    } else {
        tourSteps = tourStepsTrain; // 默认
    }

    let tourIndex = 0;
    let tourOverlay = null;

    function startTour(){
        tourIndex = 0;
        showStep();
    }

    function showStep(){
        const step = tourSteps[tourIndex];
        if(!step) return endTour();
        const target = document.querySelector(step.sel);
        if(!target) { tourIndex++; return showStep(); }

        // 清除旧高亮和旧提示框
        document.querySelectorAll('.ui-tour-highlight').forEach(el => el.classList.remove('ui-tour-highlight'));
        document.querySelectorAll('.ui-tour-tip').forEach(el => el.remove());
        target.classList.add('ui-tour-highlight');

        // 创建或清空遮罩
        if(!tourOverlay){
            tourOverlay = document.createElement('div');
            tourOverlay.className = 'ui-tour-overlay';
            document.body.appendChild(tourOverlay);
        }
        tourOverlay.innerHTML = '';

        const tip = document.createElement('div');
        tip.className = 'ui-tour-tip';
        tip.innerHTML = `<p>${step.text}</p>`;

        const btnNext = document.createElement('button');
        btnNext.textContent = (tourIndex === tourSteps.length - 1) ? '完成' : '下一步';
        btnNext.onclick = () => { tourIndex++; showStep(); };
        tip.appendChild(btnNext);
        document.body.appendChild(tip);

        // === 关键：位置逻辑，确保提示框始终在视窗内 ===
        const rect = target.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // 强制重排以获取准确尺寸
        tip.getBoundingClientRect();
        const tipRect = tip.getBoundingClientRect();
        
        // 重置所有样式
        tip.style.transform = 'none';
        tip.style.top = 'auto';
        tip.style.left = 'auto';
        tip.style.right = 'auto';
        tip.style.bottom = 'auto';
        
        // 动态计算最佳位置
        let top, left;
        let arrowTop, arrowBottom, arrowLeft, arrowRight, arrowTransform, arrowBorder;
        
        // 根据屏幕尺寸和目标位置决定提示框的放置位置
        const isMobile = viewportWidth < 768;
        const isTablet = viewportWidth < 1024;
        
        // 优先考虑屏幕中心，避免提示框靠近边缘
        if (isMobile) {
            // 移动端：提示框始终放在目标元素下方居中位置
            top = rect.bottom + window.scrollY + 15;
            left = rect.left + rect.width / 2 - tipRect.width / 2;
            
            // 箭头向上
            arrowTop = 'auto';
            arrowBottom = '-10px';
            arrowLeft = '50%';
            arrowRight = 'auto';
            arrowTransform = 'translateX(-50%)';
            arrowBorder = 'border-top: 10px solid var(--card-bg)';
        } else {
            // 桌面端：根据目标位置智能放置
            if (rect.left < viewportWidth / 2) {
                // 目标元素在屏幕左侧，提示框放右侧
                top = rect.top + window.scrollY + (rect.height - tipRect.height) / 2;
                left = rect.right + 20;
                
                // 箭头向左
                arrowTop = '50%';
                arrowBottom = 'auto';
                arrowLeft = 'auto';
                arrowRight = '-10px';
                arrowTransform = 'translateY(-50%) rotate(180deg)';
                arrowBorder = 'border-left: 10px solid var(--card-bg)';
            } else {
                // 目标元素在屏幕右侧，提示框放左侧
                top = rect.top + window.scrollY + (rect.height - tipRect.height) / 2;
                left = rect.left - tipRect.width - 20;
                
                // 箭头向右
                arrowTop = '50%';
                arrowBottom = 'auto';
                arrowLeft = '-10px';
                arrowRight = 'auto';
                arrowTransform = 'translateY(-50%)';
                arrowBorder = 'border-right: 10px solid var(--card-bg)';
            }
        }
        
        // 应用位置
        tip.style.top = `${top}px`;
        tip.style.left = `${left}px`;
        
        // 应用箭头样式
        tip.style.setProperty('--arrow-top', arrowTop);
        tip.style.setProperty('--arrow-bottom', arrowBottom);
        tip.style.setProperty('--arrow-left', arrowLeft);
        tip.style.setProperty('--arrow-right', arrowRight);
        tip.style.setProperty('--arrow-transform', arrowTransform);
        tip.style.setProperty('--arrow-border', arrowBorder);
        
        // 强制重排以获取准确尺寸
        tip.getBoundingClientRect();
        const updatedTipRect = tip.getBoundingClientRect();
        
        // 严格边界检查和调整
        // 检查右侧边界
        if (updatedTipRect.right > viewportWidth - 20) {
            tip.style.right = '20px';
            tip.style.left = 'auto';
        }
        
        // 检查左侧边界
        if (updatedTipRect.left < 20) {
            tip.style.left = '20px';
            tip.style.right = 'auto';
        }
        
        // 检查底部边界
        if (updatedTipRect.bottom > viewportHeight - 20) {
            tip.style.bottom = '20px';
            tip.style.top = 'auto';
            tip.style.transform = 'none';
            
            // 调整箭头位置到底部
            tip.style.setProperty('--arrow-top', '-10px');
            tip.style.setProperty('--arrow-bottom', 'auto');
            tip.style.setProperty('--arrow-border', 'border-bottom: 10px solid var(--card-bg)');
        }
        
        // 检查顶部边界
        if (updatedTipRect.top < 20) {
            tip.style.top = '20px';
            tip.style.bottom = 'auto';
            tip.style.transform = 'none';
            
            // 调整箭头位置到顶部
            tip.style.setProperty('--arrow-top', 'auto');
            tip.style.setProperty('--arrow-bottom', '-10px');
            tip.style.setProperty('--arrow-border', 'border-top: 10px solid var(--card-bg)');
        }
        
        // 确保提示框至少有20px的边距
        const finalTipRect = tip.getBoundingClientRect();
        if (finalTipRect.left < 20) {
            tip.style.left = '20px';
            tip.style.right = 'auto';
        }
        if (finalTipRect.right > viewportWidth - 20) {
            tip.style.right = '20px';
            tip.style.left = 'auto';
        }
        if (finalTipRect.top < 20) {
            tip.style.top = '20px';
            tip.style.bottom = 'auto';
        }
        if (finalTipRect.bottom > viewportHeight - 20) {
            tip.style.bottom = '20px';
            tip.style.top = 'auto';
        }

        // 滚动到目标元素
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });

        tourOverlay.style.pointerEvents = 'auto';
    }
    function endTour(){
        if(tourOverlay){ 
            tourOverlay.remove(); 
            tourOverlay = null; 
        }
        // 清理所有高亮和提示框
        document.querySelectorAll('.ui-tour-highlight').forEach(el => el.classList.remove('ui-tour-highlight'));
        document.querySelectorAll('.ui-tour-tip').forEach(el => el.remove());
        document.body.style.background = ''; // 确保移除任何残留样式
        document.documentElement.style.filter = ''; // 移除任何灰度滤镜（如果有）
    }

    // 工具提示（鼠标悬停时显示 data-tip）
    function initTooltips(){
        document.body.addEventListener('mouseover', (e)=>{
            const t = e.target.closest('[data-tip]');
            if(t){
                let tt = document.getElementById('ui-tooltip');
                if(!tt){ tt = document.createElement('div'); tt.id='ui-tooltip'; tt.className='ui-tooltip'; document.body.appendChild(tt); }
                tt.textContent = t.getAttribute('data-tip');
                const r = t.getBoundingClientRect();
                tt.style.left = (r.left) + 'px';
                tt.style.top = (r.top - 36) + 'px';
                tt.style.opacity = '1';
            }
        });
        document.body.addEventListener('mouseout', (e)=>{
            const tt = document.getElementById('ui-tooltip'); if(tt) tt.style.opacity='0';
        });
    }

    function initPitchDisplays(){
        document.querySelectorAll('#pitchControl').forEach(el=>{
            const valueEl = el.parentElement.querySelector('#pitchValue') || el.parentElement.querySelector('.range-value span');
            if(valueEl){
                el.addEventListener('input', ()=>{ valueEl.textContent = el.value; });
            }
        });
    }

    function init(){
        initTooltips();
        initPitchDisplays();
        loadSavedTheme();
        loadSavedFont();
    }

    return { setTheme, startTour, init, setFont, loadSavedFont };
})();

// DOM ready
window.addEventListener('DOMContentLoaded', ()=>{ UI.init(); });
