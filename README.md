# SafeHome - Джон Атанасов 2024 - 2025

SafeHome е интелигентна система за наблюдение, която използва ESP32 устройства за поточно предаване на видео и мониторинг на различни сензори като PIR сензор за движение, температура и въздух. Системата е проектирана да се интегрира с Firebase за съхранение на данни и нотификации в реално време.

## Функционалности

- **Видео наблюдение**: Система за предаване на видео поток от ESP32 камера към уеб платформа чрез ngrok или други методи.
- **Мониторинг на сензори**: Следи сензори за движение, температура и качество на въздуха.
- **Известия в реално време**: Изпращане на известия чрез Firebase, когато сензорите отчита аномалии (висока температура, замърсяване на въздуха и др.).
- **Запис на изображения**: Автоматично заснемане на изображения при открито движение и изпращане към Firebase Storage.
- **Управление на устройства**: Приложение за управление на свързаните устройства и тяхната конфигурация.

## Изисквания

- **SafeHome Camera Kit**
- **SafeHome Hub** за съхранение на данни и изображения

## Лиценз

Този проект е с отворен код и е лицензиран под [MIT лиценз](LICENSE).

## Приложение и сайт

Можете да посетите [SafeHome сайта тук](https://kvb-bg.com/SafeHome/index.php) за повече информация и актуализации.
