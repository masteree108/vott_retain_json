---
title: ' 小工具: 找出指定的timestamp 或 排除非此資料夾之*.json檔案(Windows 10)'
disqus: hackmd
---

小工具: 找出指定的timestamp 或 排除非此資料夾之*.json檔案 (Windows 10)
===

[TOC]
## 1. 工具介紹
由於 vott target 資料夾檔名複雜,若想挑出使用者指定的秒數或挑出不要的檔案(如別專案的檔案混入其中),可以使用此工具挑出指定的.json檔案
```gherkin=
目前版本:v0.0.1
```
![](https://i.imgur.com/g592TOo.png)

#### 介面說明

#### (1) start_time 
#### (2) end_time
輸入要挑出得時間,例如要從頭開始選擇十秒可輸入 
start_time: 00:00:00
end_time:00:00:10
:::warning
若兩欄都為00:00:00代表不指定 timestamp
:::
#### (3) 輸入要保留的json資料影片名稱
這是為了挑出非此專案之*.json之用途,平常使用也請輸入影片名稱,ex:Drone_014

#### (4) 選擇 json file 來源資料夾
請選擇要挑出json的專案資料夾
:::warning
如下圖,在開啟資料夾頁面會看不到檔案,請先自行知道來源資料夾的位置
:::
![](https://i.imgur.com/ztt5ppe.png)

#### (5) run 按鈕

若上述(4) 載入完成,按下 run 則會開始執行搜尋與整理
若完成後,會跳出提示訊息
![](https://i.imgur.com/wQ9PXVd.png)

## 2. 工具使用範例
請至[此處連結](https://onedrive.live.com/?authkey=%21AGKlMJQzAd8UL08&id=25CF837976B5942F%21323384&cid=25CF837976B5942F)下載來源json檔案

以下載 video14 的 00_30-00_40 來說明
![](https://i.imgur.com/AS8cG49.png)

首先開啟工具後(若有需要可直接至 7. 下載 vott_retain_json.exe 直接下載)

#### (1) 選擇來源
![](https://i.imgur.com/SJlE8tZ.png)

![](https://i.imgur.com/WLN9H34.png)

#### (2) 輸入相關資訊並按下 run 按鈕
![](https://i.imgur.com/fazgKhr.png)

等待工具完成,按下確定後工具會自行關閉
![](https://i.imgur.com/pJceHpx.png)

#### (3) 查看結果 result.xlsx
請到資料來源路徑,會多出一資料夾 not_belong_here
![](https://i.imgur.com/cSyEqRH.png)

內容如下
##### 原本資料夾位址
![](https://i.imgur.com/9h5l8zT.png)

##### not_belong_here 資料夾
多出三包資料夾分別說明如下圖
![](https://i.imgur.com/SN9gcbh.png)

![](https://i.imgur.com/V1RF5oU.png)

![](https://i.imgur.com/EsBCy6M.png)

打開 result.xlsx
##### Drone_0XX 頁籤
![](https://i.imgur.com/9qEOHfT.png)

##### not_specify_timestamp 頁籤
![](https://i.imgur.com/Sx7QDJB.png)

##### other_sources 頁籤
由於這個範例無混入其他*.json檔案,以其他專案當範例
顯示非此專案之*.json檔案
![](https://i.imgur.com/FxuLHPA.png)

##### empty_timestamp_json 頁籤
![](https://i.imgur.com/j4HN7of.png)
實際開啟此檔案如下,只有框架無使用者標註之內容
![](https://i.imgur.com/oN45Dd8.png)


## 3. 環境架設
:::info
若直接使用可不必架設環境與下載source code,可直接跳至7.下載
:::
請參考 [此連結項目](https://hackmd.io/@NTUTVOTT/SJ4I5lhF_) 進行環境架設

## 4. source code github 位址
[github 連結](https://github.com/masteree108/vott_retain_json)

```gherkin=
http:
git clone https://github.com/masteree108/vott_retain_json.git 

ssh:
git clone git@github.com:masteree108/vott_retain_json.git
```
## 5. 執行 source code
打開 Anaconda Promot(anaconda3) 進入source code 資料夾
![](https://i.imgur.com/7ZMnbiB.png)

下圖只是範例,請至自己電腦的 source code 下載資料夾
![](https://i.imgur.com/g7CKg9z.png)
```gherkin=
python main.py
```

## 6. 製作 vott_retain_json.exe
:::info
注意,只有在ubuntu下才能直接使用./build_exe.sh
:::
若要製作 vott_retain_json.exe ,首先開啟 Anaconda Promot(anaconda3)並切換環境
```gherkin=
conda activate your_env
pyinstaller -F ./main.py
```
製作完成後,將產生的./dist/main.exe 複製到別處並更名,最後刪除不必要的暫存檔
:::info
注意,以下的指令必須在 WSL 的 ubuntu 底下執行
:::
關於WSL ubuntu 安裝請參考[此連結](https://hackmd.io/@NTUTVOTT/BkRrY457d)
將以下的指令貼在 WSL ubuntu terminal 上
```gherkin=
cp ./dist/main.exe ./ && mv main.exe vott_retain_json.exe && rm -rf dist && rm -rf __pycache__ && rm -rf build && rm *.spec
```
## 7. 下載 vott_retain_json.exe
```gherkin=
目前版本:v0.0.1
```
[工具下載連結](https://drive.google.com/drive/folders/1bCgvqK7sGGL9RR58UUg3QbaAFUUrRVdv?usp=sharing)

###### tags: `tool`, `Python`