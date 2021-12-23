# 指定の動画を指定の始点終点で切り出して、元動画と同じディレクトリに別名の動画として出力する

# 参考URL
# https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html


from PySimpleGUI.PySimpleGUI import Window
import moviepy.editor as mp
import PySimpleGUI as sg
import os, datetime, sys

this_software_name = "simple_movie_cut_editor"

# 時、分、秒のリストを与えると、合計秒数を返す。エラーの場合は-1を返す
def total_sec(hh_mm_ss:list):
    try:
        return (datetime
                .timedelta(hours=int(hh_mm_ss[0] or 0), minutes=int(hh_mm_ss[1] or 0), seconds=int(hh_mm_ss[2] or 0)) # 空文字列の場合も0を返すようにする
                .total_seconds()
                )
    except:
        return -1


# 入力用ウィンドウを表示し、ユーザーの入力を返す
def input_by_user(default_movie_path:str):
    layout = [[sg.T("カット抽出する動画"), sg.InputText(default_text=default_movie_path, key="movie_path"), sg.FileBrowse(target="movie_path")],
                [sg.T("抽出区間 (時:分:秒)"),
                sg.Spin([i for i in range(1000)], key='hh_s', size=(4,1)),
                sg.Spin([i for i in range(61)], key='mm_s', size=(3,1)),
                sg.Spin([i for i in range(61)], key='ss_s', size=(3,1)), sg.T("~"),
                sg.Spin([i for i in range(1000)], key='hh_e', size=(4,1)),
                sg.Spin([i for i in range(61)], key='mm_e', size=(3,1)),
                sg.Spin([i for i in range(61)], key='ss_e', size=(3,1))],
                [sg.Button("OK", bind_return_key=True, size=(6,1))]]
    window = sg.Window(this_software_name, layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            sys.exit()
        elif event == "OK":
            movie_file_path = values["movie_path"] # InputTextの値を取得する。FileBrowseにキーを設定して値を取得すると、default_movie_pathのまま実行したとき値を取得できない
            movie_file_name = os.path.splitext(movie_file_path)[0].split('/')[-1]
            movie_file_extension = os.path.splitext(movie_file_path)[1]
            start_time_list = [values["hh_s"], values["mm_s"], values["ss_s"]] # 再生開始時間
            end_time_list = [values["hh_e"], values["mm_e"], values["ss_e"]] # 再生終了時間
            
            # 入力動画ファイルをチェック
            try:
                mp_obj = mp.VideoFileClip(movie_file_path)
            except:
                sg.popup("動画ファイルを読み込めません。正しいファイルを指定しているか確認してください", no_titlebar=True)
                continue

            start_sec = total_sec(start_time_list)
            end_sec = total_sec(end_time_list)

            # カット位置をチェック
            if start_sec == -1 or end_sec == -1 or start_sec >= end_sec or start_sec >= mp_obj.duration:
                sg.popup(f"抽出区間が有効ではありません。入力し直してください", no_titlebar=True)
                continue

            window.close()

            return mp_obj, movie_file_path, movie_file_name, movie_file_extension, start_time_list, end_time_list


# 保存した動画を指定再生時間で抽出し、元動画のディレクトリに別名出力する
def trim_video(mp_obj, movie_file_name:str, movie_file_extension:str, start_time_list:list, end_time_list:list):
    # 指定再生時間を秒数に直す
    start_sec = total_sec(start_time_list)
    end_sec = total_sec(end_time_list)

    # 終了時間が動画時間を超える場合、終点に合わせる
    if end_sec > mp_obj.duration:
        end_sec = mp_obj.duration
        
        end_time_list = list(map(int, [end_sec//3600, (end_sec%3600)//60, end_sec%60])) # 動画時間の時分秒表記

    start_time_str = "".join(list(map(lambda x: str(x).zfill(2), start_time_list))) # 抽出開始時間のhhmmss表記
    end_time_str = "".join(list(map(lambda x: str(x).zfill(2), end_time_list))) # 抽出終了時間のhhmmss表記
    
    # 動画を切り出し、切り出し位置付きの別名で保存する
    clip = mp_obj.subclip(start_sec, end_sec)
    clip.write_videofile(f"{movie_file_name}_{start_time_str}_{end_time_str}{movie_file_extension}") # 抽出区間をファイル名に入れて動画を出力
    clip.close()

    sg.popup("抽出が完了しました", no_titlebar=True)


def main():
    global default_movie_path
    global default_output_folder
    default_movie_path = ""
    try:
        while 1: # 連続で切り出せるようにループ
            mp_obj, movie_file_path, movie_file_name, movie_file_extension, start_time_list, end_time_list = input_by_user(default_movie_path)
            trim_video(mp_obj, movie_file_name, movie_file_extension, start_time_list, end_time_list)
            default_movie_path = movie_file_path

    except SystemExit:
        pass

    except:
        sg.popup("予期しないエラーが発生しました。プログラムを終了します", no_titlebar=True)


if __name__ == "__main__":
	main()