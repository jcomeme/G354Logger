# G354Logger

## 概要
M-G354の評価キットがMacで使えなかったので、まずはMacでログが取れればいいかと思って作りました。

シリアル通信にはpyserialを使用しています。

このプログラムでは200SPSで動作すると思いますが、

```
controller.writeRegister(b'\x05', b'\x09', b'\x01')#dout rate 設定。00で2000SPS, 値が1増えるごとに1/2になる
↓
controller.writeRegister(b'\x05', b'\x00', b'\x01')
```

このように改変すれば2000SPSで動作します。

出力のフォーマットは

| アドレス | 温度 | ジャイロX　| ジャイロY　| ジャイロZ | 加速度X　| 加速度Y　| 加速度Z |番号| デリミタ |
-------------|---- |---|---|---|---|---|---|---|---

このような順番になってますが、数字の処理がほんとに合ってるかちょっとあやしい。間違ってたら教えてほしいです。
ジャイロと加速度の値は16bitで取ってます。


## 使い方

```
python logger.py
```


止める時はCtrl-Cで。

## 動作確認環境

Pythonは3.7.0を使用しています。2系だとうまく動かないかも。
シリアル通信にはpyserialを使っています。
USB評価ケーブルM-C30EV041と、評価ボードM-G32EV031を使って確認していますが、普通にPCからシリアル接続できれば問題なく使えると思います。


