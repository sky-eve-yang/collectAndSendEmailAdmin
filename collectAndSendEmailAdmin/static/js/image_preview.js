document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.cert-preview').forEach(function(imgElement) {
        imgElement.parentElement.addEventListener('click', function(e) {
            e.preventDefault();
            var img = new Image();
            img.style.maxWidth = '80%';  // 控制图片最大宽度
            img.style.maxHeight = '80vh'; // 控制图片最大高度
            img.onload = function() {
                var lightbox = document.createElement('div');
                lightbox.style.position = 'fixed';
                lightbox.style.top = '50%';
                lightbox.style.left = '50%';
                lightbox.style.transform = 'translate(-50%, -50%)';
                lightbox.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                lightbox.style.padding = '10px';
                lightbox.style.borderRadius = '8px';
                lightbox.style.display = 'flex';
                lightbox.style.justifyContent = 'center';
                lightbox.style.alignItems = 'center';
                lightbox.style.zIndex = '1000';

                var closeBtn = document.createElement('button');
                closeBtn.textContent = '✕';
                closeBtn.style.position = 'absolute';
                closeBtn.style.top = '10px';
                closeBtn.style.right = '10px';
                closeBtn.style.color = '#fff';
                closeBtn.style.border = 'none';
                closeBtn.style.background = 'transparent';
                closeBtn.style.fontSize = '30px';
                closeBtn.style.cursor = 'pointer';
                closeBtn.style.outline = 'none';

                closeBtn.onclick = function() {
                    document.body.removeChild(lightbox);
                };

                lightbox.appendChild(img);
                lightbox.appendChild(closeBtn);
                document.body.appendChild(lightbox);
            };
            img.src = e.target.parentElement.href;
        });
    });
});
