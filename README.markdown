# DefenseGridCaptionMOD 取扱説明書

## DefenseGridCaptionMODの機能と目的
DefenseGridCaptionMODは、[Hidden Path Entertainment](http://www.hiddenpath.com/)から発売されているWindows用ゲーム『[Defense Grid: The Awakening](http://www.hiddenpath.com/games/defense-grid/)』の、字幕のテキストとフォントを書き換えることができます。英語字幕から日本語字幕に書き換えることを、主な目的としています。

## DefenseGridCaptionMODの使用上の注意
**DefenseGridCaptionMODの動作はまだ十分に検証されていない**ため、取り返しのつかない問題を発生させてしまうことがあるかもしれません。**動作の結果に自己責任で対応**できる方のみ、DefenseGridCaptionMODを使用してください。

## DefenseGridCaptionMODをインストールする手順

### 1. 『Defense Grid: The Awakening』のインストール
Windows用『Defense Grid: The Awakening』を任意のディレクトリにインストールしてください。以後このディレクトリを**"DefenseGrid/"**と表記します。

### 2. DefenseGridCaptionMODの入手
1. [DefenseGridCaptionMOD - GitHub](http://github.com/psychi/DefenseGridCaptionMOD/)にある「Download」ボタンを押して、圧縮ファイルをダウンロードして下さい。ダウンロードする圧縮ファイルはzip形式とtar.gz形式を選べますが、どちらをダウンロードしても構いません。
2. ダウンロードした圧縮ファイルを、任意のディレクトリに展開してください。ただし、**展開先ディレクトリの絶対パス名には、全角文字が含まれない**ようにしてください。以後このディレクトリを**"DefenseGridCaptionMOD/"**と表記します。

### 3. 『Defense Grid: The Awakening』のオリジナルデータのコピー
1. **"DefenseGridCaptionMOD/"**の直下に、**"input_dgp"**と**"output_dgp"**の2つのディレクトリを作ってください。
2. **"DefenseGrid/"**の直下にあるファイルのうち、ファイル名の拡張子が**dgp**となっているものすべてを、**"DefenseGridCaptionMOD/input_dgp/"**の直下にコピーしてください。

### 4. 日本語フォントの入手
Windowsのコントロールパネルからフォントを開いて、「メイリオ レギュラー（meiryo.ttc）」と「メイリオ ボールド（meiryob.ttc）」の2つを、**"DefenseGridCaptionMOD/"**の直下にコピーしてください。

### 5. "swfmill.exe"の入手
[swfmill公式サイト](http://swfmill.org/)から[Windows用swfmillバイナリ](http://swfmill.org/releases/swfmill-0.3.1-win32.zip)をダウンロードし、その中に含まれている**"swfmill.exe"**を、**"DefenseGridCaptionMOD/"**の直下にコピーしてください。

### 6. "dgridhash.exe"の入手
[Luigi Auriemma氏のウェブサイト](http://aluigi.altervista.org/papers.htm#others-file)から[DefenseGrid dgp files hash calculator](http://aluigi.altervista.org/papers/dgridhash.zip)をダウンロードし、その中に含まれている**"dgridhash.exe"**を、**"DefenseGridCaptionMOD/"**の直下にコピーしてください。

以上で、DefenseGridCaptionMODのインストールは完了です。

## 『Defense Grid: The Awakening』の字幕を日本語化する手順

### 1. 字幕のテキストとフォントを日本語に書き換える
**"DefenseGridCaptionMOD/MakeCaptionsAndFonts.bat"**をファイルエクスプローラでダブルクリックし、実行が終了するまで待機してください。字幕のテキストとフォントのデータを、自動で書き換えます。

* 環境にもよりますが、10分ほど時間がかかります。
* メモリを大量に必要とするので、実行が終了するまでは他の作業を行わないことを推奨します。

### 2. 書き換えたデータをコピー
**"DefenseGridCaptionMOD/output_dgp"**の直下にあるすべてのファイルを、**"DefenseGrid/"**の直下にコピーしてください。

以上で、『Defense Grid: The Awakening』の字幕が日本語で表示されるようになります。

## 『Defense Grid: The Awakening』の字幕を日本語に翻訳する作業のお願い
現在、『Defense Grid: The Awakening』の字幕を日本語に翻訳する作業は途中となっています。

より多くの方が翻訳作業を行えるように、[DGTA翻訳作業シート](https://spreadsheets.google.com/spreadsheet/ccc?key=0Al6UoUVkZrnXdG9uR1VyU0tPMU1QQUgwcGpYbWQ1YlE&hl=ja&pli=1#gid=1)を、有志の方が用意されています。翻訳に協力していただける方は、このスプレッドシートを編集して、原文を日本語に翻訳してみてください。

以下の手順で、編集したスプレッドシートをDefenseGridCaptionMODで使うことができます。

1. [DGTA翻訳作業シート](https://spreadsheets.google.com/spreadsheet/ccc?key=0Al6UoUVkZrnXdG9uR1VyU0tPMU1QQUgwcGpYbWQ1YlE&hl=ja&pli=1#gid=1)にあるメニュバーから、「ファイル」→「形式を指定してダウンロード」→「OpenOffice」を選択し、odsファイルをダウンロードして下さい。
2. ダウンロードしたodsファイルを、**"DefenseGridCaptionMOD/DefenseGridCaptionMOD.ods"**に上書きしてください。
3. 前節の**『Defense Grid: The Awakening』の字幕を日本語化する手順**に従って作業をすすめてください。

## 2011.12.07以前から使っている方へ
2011.12.07に『Defense Grid: The Awakening』のプログラムに大きな更新がありました。この更新によって以前のdgpファイルが使えなくなったらしく、DefenseGridCaptionMODを適用した状態の『Defense Grid: The Awakening』が起動しなくなっていたようです。

2011.12.07以前からDefenseGridCaptionMODを使っていた方は、以下の手順で更新を行なってください。

1. DefenseGridCaptionMODの最新版を取得してください。

2. **"DefenseGridCaptionMOD/input_dgp/"**以下にあるdgpファイルをすべて削除してください。

3. 『Defense Grid: The Awakening』を一度アンインストールしてから、再度インストールしてください。

4. **"DefenseGrid/"**の直下にあるファイルのうち、ファイル名の拡張子が**dgp**となっているものすべてを、**"DefenseGridCaptionMOD/input_dgp/"**の直下にコピーしてください。

5. 「『Defense Grid: The Awakening』の字幕を日本語化する手順」を実行してください。

以上です。
