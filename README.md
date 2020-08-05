# PythonとGDALを使ってウェッブマップを作ろう

オープンソースのPythonとGDALを使って無償でGISデータを処理する方法を紹介します。今回使用するデータは国土地理院が提供している<a href="https://fgd.gsi.go.jp/download/menu.php">基盤地図情報</a>の数値標高モデル。

[![](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/677829/523a02a2-b6b5-6a22-c7b2-76773c887a27.png)](https://danielhoshizaki.github.io/hillshade/)

PythonとGDALの組み合わせで上記のウェッブマップが作成されます。

#### インストール
まずは<a href="https://docs.conda.io/en/latest/miniconda.html">Miniconda</a>を使ってPythonと必要なライブラリをインストールしましょう。ダウンロードが完了したと後はMinicondaのコマンドラインを開きPythonの仮想環境を立ち上げます（デフォルトのPython3バージョンを使用）：

```
conda create --name myenv
conda activate myenv
```

次にPythonのスクリプトに使用するライブラリをインストールします：

```
conda install -c conda-forge gdal numpy beautifulsoup4
```

最後にウェッブマップ作製に使用するPythonのスクリプトをダウンロードします：

```
git clone https://github.com/danielhoshizaki/hillshade
```

#### 使い方
まずは```./data/raw```ディレクトリに数値標高モデルファイルがあることを確認しましょう。他のファイルをダウンロードしている場合はこの段階で```./data/raw```の中に置きます。

Pythonスクリプトを回す前にコードの一部を変える必要があります。```conda```でインストールしたライブラリGDALのパスを指定する必要があります。GDALは協力なソフトですがインストールが非常に複雑である為今回は絶対パスを使いましょう。GDALのバイナリーを探すにはLinuxの```find```を使うかWindosの検索ボックスを使います。上記で作成したmyenv仮想環境のディレクトリを探せばすぐに出てきます。探すのはgdaldem.exeとgdalbuildvrt.exeが入っているはディレクトリとgdal2tiles.pyが入っているディレクトリ。見つけたらPythonスクリプトのgdal_bin_pathとgdal_tiles_pathを設定します。

準備が整ったらスクリプトを起動してウェッブマップが出来るのを待ちます。

#### 仕組み
Pythonスクリプトは大きく分けて二つの役割を果たしています。一つは```convert```と言うファンクションを使って生の数値標高モデルファイル（ZIPされたXMLファイル）をGeoTiffに変換すること。二つめの役割はコマンドラインを通してGDALに直接データを処理してもらうこと。GDALに直接流すコマンドは三つあります以下のデータ処理が行われます：

1. 各DEMのGeoTiffを陰影起伏GeoTiffに変換
2. 全ての陰影起伏GeoTiffをバーチャルデータセットvrtにまとめる
3. バーチャルデータセットをウェッブマップに変換

最後に回すgdal2tilesコマンドは新規に```./data/WTMS```ディレクトリを作ります。ディレクトリの中にはLeaflet.htmlと言うファイルがあるのでダブルクリックをしましょう。独自のウェッブマップが完成です！ただしこのウェッブマップは自分のPCで見ることしかできません.. 他の人にも見てもらい場合はGithub PagesやAWS S3に乗せるかもうちょっと頑張ってウェッブサバーに乗せてみましょう！
