# 指定URLのyoutube動画を指定拡張子で指定保存場所にDLする
# https://pytube.io/en/latest/api.html

import PySimpleGUI as sg
import os, re, sys
from pytube import YouTube


this_software_name = "youtube_simple_downloader"

executed_from_pyfile = True # pyファイルで実行する場合はTrue、exeファイル化して実行する場合はFalse

if executed_from_pyfile:
    default_output_folder = os.path.dirname(os.path.abspath(__file__))
else:
    default_output_folder = os.path.dirname(sys.executable)


# 入力用ウィンドウを表示し、ユーザーの入力を返す
def input_by_user(default_output_folder:str):
    layout = [[sg.T('YouTube動画URL'), sg.Input(key="url", size=(60,1))],
                [sg.T('保存形式'+' '*12), sg.Combo(('動画(mp4)', '音声(mp3)'), default_value='動画(mp4)', size=(10,1), key="file_extension")],
                [sg.T('出力先フォルダ'+' '), sg.In(size=(53,1), enable_events=True, key='-FOLDER-', default_text=default_output_folder), sg.FolderBrowse("選択")],
                [sg.Button("OK", bind_return_key=True, size=(6,1))]]
    window = sg.Window(this_software_name, layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            sys.exit()
        elif event == "OK":
            url = values["url"] # DLするyoutube動画のURL
            output_folder = values["-FOLDER-"] # 出力フォルダ

            file_extension_dict = {"動画(mp4)":"mp4", "音声(mp3)":"mp3"}
            file_extension = file_extension_dict[values["file_extension"]] # 拡張子
            
            # 有効な入力値かチェックする
            try:
                yt = YouTube(url)
            except:
                sg.popup("動画にアクセスできません。URLを確認して再入力してください", no_titlebar=True)
                continue
            
            # 有効な出力先フォルダかチェックする
            if os.path.isdir(output_folder):
                pass
            else:
                sg.popup("出力先フォルダが見つかりません。有効なフォルダを指定してください", no_titlebar=True)
                continue

            window.close()
            return file_extension, output_folder, yt


# YouTube Objectから与えられる変数を受けてDL進捗状況を表示する
######### pyinstallerを使用してexe化すると機能しない模様？
def progress_Check(stream=None, chunk=None, bytes_remaining=None):
    file_size = stream.filesize
    if bytes_remaining == None: # 初期状態で0%を出力(bytes_remaining==None)
        percent = 0.0
    else:
        percent = round(100 * (1 - bytes_remaining/file_size), 1)

    # ループ処理なしに進捗状況を表示する方法がデバッグウィンドウしか見つからなかった
    # erase_all=Trueとするとエラー(最初の1回しか出ないので白紙をクリアーするとエラーが出る？)
    sg.Print(f"{percent}% ダウンロード完了", size=(25,10), do_not_reroute_stdout=False, no_button=True)


# 出力先フォルダ、拡張子、YouTube Objectを与えると、URLの動画を指定拡張子で保存する
def dl_video(output_folder:str, file_extension:str, yt):
    video_title = re.sub(r'[\\/:*?"<>|]+','',yt.title) # 動画タイトルから記号を削除
    if file_extension == "mp4":
        yt.register_on_progress_callback(progress_Check) # 進捗表示。動画DL済みの場合は表示されない
        (yt
        .streams
        .filter(file_extension=file_extension)
        .get_highest_resolution() # 最高画質
        .download(output_folder, filename=f"{video_title}.{file_extension}")
        )
    else: # mp3。register_on_progress_callbackには非対応の模様
        (yt
        .streams
        .get_audio_only() # デフォルトで最高音質
        .download(output_folder, filename=f"{video_title}.{file_extension}")
        )
    return


def main():
    try:
        file_extension, output_folder, yt = input_by_user(default_output_folder)
        dl_video(output_folder, file_extension, yt)
        sg.popup("ダウンロードが完了しました", no_titlebar=True)
    except SystemExit:
        pass
    except:
        sg.popup("予期しないエラーが発生しました。プログラムを終了します", no_titlebar=True)


if __name__ == "__main__":
	main()