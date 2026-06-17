# 環境構築

## ローカルにcloneする
1. ローカルの親ディレクトリに移動する
```
cd C:\Users\ctc\Documents\Workspaces
```

2. git cloneする
```
git clone https://github.com/tyuya1173/summerlin.git
```

3. データベースを作る
```
mysql > create database summerlin;
mysql > use summerlin;
```

4. マイグレートする
```
python manage.py makemigrations
python manage.py migrate
```

5. テストデータを入れる
```
python manage.py seed --clean
```

6. developブランチにチェックアウトする
```
git checkout develop
```

## ブランチ運用
1. developブランチに移動
```
git checkout develop
```

2. developブランチを最新版にする
```
git pull
```

3.  開発するときにブランチをきる
```
git checkout -b ブランチ名
```

4. 開発が完了したらプッシュする
```
git add .
git commit -m "コミットメッセージ"
git push origin ブランチ名
```

5. pull requestを書く
githubに移動して、Pull Requestを作成