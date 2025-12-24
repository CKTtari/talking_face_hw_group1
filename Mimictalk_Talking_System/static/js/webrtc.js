// 简单 WebRTC 占位脚本，负责采集本地摄像头并显示在页面左侧（仅示例，需后端/信令服务器支持）

const WebRTC = (function(){
    let localStream = null;
    async function startLocalVideo(elementId){
        try{
            const el = document.getElementById(elementId);
            if(!el) return;
            localStream = await navigator.mediaDevices.getUserMedia({video:true,audio:true});
            const video = document.createElement('video');
            video.autoplay = true; video.muted = true; video.playsInline = true;
            video.srcObject = localStream;
            el.innerHTML = ''; el.appendChild(video);
        }catch(e){
            console.warn('无法访问摄像头：', e);
        }
    }
    function stopLocal(){ if(localStream){ localStream.getTracks().forEach(t=>t.stop()); localStream=null; } }
    return { startLocalVideo, stopLocal };
})();

// 不再自动启动视频预览，改为由用户点击"开始对话"按钮启动
// 这样可以更好地控制用户隐私和权限请求时机