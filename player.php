<?php
/* حماية بسيطة */
if (!isset($_GET['url'])) {
    die("NO STREAM");
}
$stream = htmlspecialchars($_GET['url']);
?>
<!DOCTYPE html>
<html lang="ar">
<head>
<meta charset="UTF-8">
<title>MYCIMA PLAYER</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>

<style>
html,body{
    margin:0;
    width:100%;
    height:100%;
    background:#000;
    overflow:hidden;
}
video{
    width:100%;
    height:100%;
    background:#000;
    object-fit:contain;
}
#msg{
    position:absolute;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    color:#0ff;
    font-size:16px;
}
.credit{
    position:absolute;
    bottom:8px;
    right:10px;
    font-size:11px;
    color:#aaa;
}
</style>
</head>

<body>

<video id="video" controls autoplay></video>
<div id="msg">جاري التحميل...</div>
<div class="credit">Developed by M_1Y_M</div>

<script>
const video = document.getElementById("video");
const msg   = document.getElementById("msg");
const url   = "<?php echo $stream ?>";

if(Hls.isSupported()){
    const hls = new Hls({
        lowLatencyMode:true,
        backBufferLength:90
    });
    hls.loadSource(url);
    hls.attachMedia(video);

    hls.on(Hls.Events.MANIFEST_PARSED,()=>{
        video.play();
        msg.style.display="none";
    });

    hls.on(Hls.Events.ERROR,()=>{
        msg.innerText="خطأ في البث";
    });

}else if(video.canPlayType("application/vnd.apple.mpegurl")){
    video.src = url;
    video.play();
    msg.style.display="none";
}else{
    msg.innerText="المتصفح لا يدعم HLS";
}
</script>

</body>
</html>
