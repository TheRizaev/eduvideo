// Код для инициализации KronikPlayer при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM загружен, проверка наличия элементов плеера...");
    
    // Проверяем наличие элемента видеоплеера
    const videoElement = document.getElementById('kronik-player');
    if (!videoElement) {
        console.error('Элемент видеоплеера не найден на странице!');
        return;
    }
    
    console.log("Элемент плеера найден, проверка загрузки VideoJS...");
    
    // Проверка загрузки VideoJS
    if (typeof videojs === 'undefined') {
        console.error('VideoJS не загружен! Проверьте, что скрипт video.min.js подключен корректно.');
        // Добавляем скрипт динамически
        const vjsScript = document.createElement('script');
        vjsScript.src = 'https://vjs.zencdn.net/7.20.3/video.min.js';
        vjsScript.onload = initKronikPlayer;
        document.head.appendChild(vjsScript);
        return;
    }
    
    // Первичная проверка KronikPlayer
    initKronikPlayer();
    
    function initKronikPlayer() {
        console.log("VideoJS загружен, проверка KronikPlayer...");
        
        // Проверяем, загружен ли KronikPlayer
        if (typeof KronikPlayer === 'undefined') {
            console.error('KronikPlayer не определен! Загружаем заново...');
            
            // Загружаем скрипт KronikPlayer динамически
            const kronikScript = document.createElement('script');
            kronikScript.src = '/static/js/video-player.js';
            kronikScript.onload = function() {
                console.log('KronikPlayer загружен динамически');
                initializePlayer();
            };
            document.head.appendChild(kronikScript);
        } else {
            console.log('KronikPlayer определен, инициализация...');
            initializePlayer();
        }
    }
    
    function initializePlayer() {
        try {
            // Получаем идентификатор видео из URL
            let videoId = window.location.pathname.split('/').filter(Boolean)[1] || 'default-video';
            
            // Ищем связанные видео для функции "Следующее видео"
            const relatedVideos = document.querySelectorAll('.related-video-card');
            const nextVideoSelector = relatedVideos.length > 0 ? '.related-video-card:first-child' : null;
            
            console.log(`Инициализация KronikPlayer с ID видео: ${videoId}, найдено связанных видео: ${relatedVideos.length}`);
            
            // Инициализируем плеер с настройками
            window.kronikPlayerInstance = new KronikPlayer('kronik-player', {
                videoId: videoId,
                showNextVideo: true,
                nextVideoSelector: nextVideoSelector,
                nextTitleSelector: '.related-title',
                nextChannelSelector: '.related-channel',
                trackWatchProgress: true,
                trackWatchComplete: true
            });
            
            console.log('KronikPlayer успешно инициализирован!');
            
            // Добавляем пользовательское событие, чтобы другие скрипты могли узнать о инициализации
            document.dispatchEvent(new CustomEvent('kronikPlayerReady', { 
                detail: { player: window.kronikPlayerInstance }
            }));
        } catch (err) {
            console.error('Ошибка при инициализации KronikPlayer:', err);
            
            // Запасной вариант - использовать стандартный VideoJS
            try {
                console.log('Пробуем инициализировать стандартный VideoJS как запасной вариант...');
                const player = videojs('kronik-player');
                console.log('Стандартный VideoJS плеер инициализирован как запасной вариант');
            } catch (err2) {
                console.error('Критическая ошибка при инициализации стандартного VideoJS:', err2);
            }
        }
    }
});

// Если страница уже загружена, инициализируем сразу
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('Страница уже загружена, инициализируем плеер немедленно');
    const initEvent = new Event('DOMContentLoaded');
    document.dispatchEvent(initEvent);
}