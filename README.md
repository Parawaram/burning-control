# Burning Control

## Запуск

```bash
source backend/venv/bin/activate
sudo backend/venv/bin/python startup.py
```

Для автоматического запуска при загрузке Raspberry Pi скопируйте файл
`burning-control.service` в `/etc/systemd/system/` и выполните:

```bash
sudo systemctl enable burning-control.service
sudo systemctl start burning-control.service
```

## OLED дисплей

Модуль `oled_small.py` использует дисплей SSD1306 64x48.
Он подключается к шине I²C (SCL и SDA). Кнопки "влево" и "вправо"
подключены к выводам D5 и D6 соответственно. Адрес дисплея по умолчанию
`0x3C`.

## Светодиодная лента

Файл `neopixel_controller.py` настроен на 7 диодов, подключённых к пину GPIO18.
Яркость ограничена значением `0.5` и может регулироваться через веб-интерфейс.
Для полного выключения используйте кнопку **Off**.
