
pyusb を使用した Android Open Accessory (AOA) 機器の実装サンプルです。


# Environment 

以下の環境で動作を確認しています。
* Raspberry Pi Zero W
* Raspberry Pi OS Lite
* Python 3.13
* PyUSB

Raspberry Pi Zero W を使用する場合、セルフパワー方式のUSBハブを使用すると安定するようです。
USB_micro_Bオス - USB_Aメス、のような変換ケーブルでも通信できましたが、抜き差しをすると再起動することがあります。


# Setup

## python 環境
setup.sh を実行すると、python環境を作成します。

```
$ bash setup.sh
```

## USB操作の権限

以下を実施してください。

```
$ sudo vi /etc/udev/rules.d/99-android-aoa.rules
SUBSYSTEM=="usb", MODE="0660", GROUP="plugdev"

$ sudo udevadm control --reload-rules
$ sudo udevadm trigger
```


# Files

src ディレクトリにスクリプトと設定ファイルを配置しています。

* main.py ... エントリポイント。USBデバイスを検出し、AOAモードへ切り替える。
* aoa_loopback.py ... AOA確立後の通信のみを実装したスクリプト。設定ファイルで差し替えできる。
* config.toml ... 設定ファイル。(AOAデバイスの情報など)


# Run

```
$ source .venv/bin/activate
(.venv) $ python src/main.py
```


