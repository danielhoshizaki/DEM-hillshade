# PythonとGDALを使ってウェッブマップを作ろう

GISデータの処理に多いに役立つオープンソースソフトと言語を紹介します。今回使用するデータは国土地理院が提供している<a href="https://fgd.gsi.go.jp/download/menu.php">基盤地図情報</a>の数値標高モデル。

[![](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/677829/523a02a2-b6b5-6a22-c7b2-76773c887a27.png)](https://danielhoshizaki.github.io/hillshade/)

PythonとGDALの組み合わせで上記のウェッブマップが作成されます。

### インストール
Pythonを四年程使っていますが一番楽な方法はAnacondaです（多くのOS環境で使用可能）。Anacondaは割と重いので<a href="https://docs.conda.io/en/latest/miniconda.html">Miniconda</a>を使ってインストールしましょう。ダウンロードが完了したとあとはMinicondaのコマンドラインを開きPythonの仮想環境を立ち上げます（デフォルトのPython3バージョンを使用）：

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
