from __future__ import unicode_literals
import streamlit as st
import pandas as pd
import base64
import os
from io import BytesIO
import pysrt
from datetime import datetime, timedelta
import sys
import time


#-----------------------SRT to Excel-------------------
def srttoexcel():
    subs = pysrt.open('captions.srt')
    row_list=[]
    for i in range(len(subs)):
        text = subs[i].text
        start = subs[i].start
        str_start = str(start)
        start_interval = datetime.strptime(str_start, "%H:%M:%S,%f")
        str_start_second = format(start_interval, '%H:%M:%S')
        str_start_millisecond = format(start_interval, '%f')
        end = subs[i].end
        str_end = str(end)
        end_interval = datetime.strptime(str_end, "%H:%M:%S,%f")
        str_end_second = format(end_interval, '%H:%M:%S')
        str_end_millisecond = format(end_interval, '%f')
        row_list.append([text,str_start_second,str_start_millisecond,str_end_second,str_end_millisecond])


    df = pd.DataFrame(row_list)
    df[2] = df[2].astype('str')
    df[4] = df[4].astype('str')
    return df


def exceltosrt(full_df, refLang1, lang1):
    #full_df = pd.read_excel('subs.xlsx', header=None, dtype=str)
    full_df.columns = [refLang1,'1','2','3','4']
    #lang = lang
    #Get subs file
    #xlsx=pd.read_csv('Translation - Lyric Library.csv')
    xlsx=df
    xlsx_link=xlsx[[refLang1,lang1]]

    check = full_df.merge(xlsx_link, on=refLang1, how='left')
    xlsx = check[[lang1,'1','2','3','4']]

    sheet1 = xlsx
    sheet1.columns = ["text", "start", "start_milli", "end", "end_milli"]


    counter = 1
    with open(lang1+".srt", 'w', encoding='utf-8') as file:
        for index, row in sheet1.iterrows():
            milli1 = str(row['start_milli'])[:-3]
            milli2 = str(row['end_milli'])[:-3]
            print("%d\n%s,%s --> %s,%s\n%s\n" % (
                counter, row["start"], milli1, row["end"], milli2, row["text"]), file=file)
            counter += 1
    return(lang1)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

#"""Used to write the page in the app.py file"""
st.set_option('deprecation.showfileUploaderEncoding', False)
with st.spinner("Loading ..."):
    #title of microservice
    #st.image('kingdomcity.gif')
    st.title('Translation SRT')
    #password = st.text_input("Enter a password", type="password")

    st.sidebar.title("Translation Library")

    st.sidebar.info("Upload the Lyric Library and Reference SRT")

    #Upload LyricLibrary
    lyriclibary = st.sidebar.file_uploader("Upload Lyric Library CSV File:", key = 'a', type=("csv"))
    if lyriclibary is not None:
        lyriclibary.seek(0)
        try:
            with st.spinner("Uploading your Lyric Library..."):
                df = pd.read_csv(lyriclibary)#, dtype=str)
                df = df.fillna('')
                lan_list = df.columns.tolist()
                refLang = st.sidebar.selectbox("Select reference language", lan_list)
                lan_list.remove(refLang)

                #st.success('Done!')
            st.subheader("Lyric Library")
            st.write(df)

        except Exception as e:
            st.error(
                f"Sorry, there was a problem processing your Lyric Library./n {e}"
            )
            lyriclibary = None

        #data = df


    if lyriclibary is not None:
        lyriclibary.seek(0)
        #Upload English SRT
        english_subs = st.sidebar.file_uploader("Upload Reference SRT File:")#, key = 'a', type=("srt"))
        if english_subs is None:
            st.write("Please upload Reference SRT")
        else:
            english_subs.seek(0)
            try:
                with st.spinner("Loading SRT..."):
                    g = BytesIO(english_subs.read())  ## BytesIO Object
                    temporary_location = "captions.srt"

                    with open(temporary_location, 'wb') as out:  ## Open temporary file as bytes
                        out.write(g.read())  ## Read bytes into file
                    # close file
                    out.close()
                    data = srttoexcel()
                    lang = st.selectbox("Select language to download", lan_list)
                    if exceltosrt(data, refLang, lang) == lang:
                        if st.button('Process'):
                            st.markdown(get_binary_file_downloader_html(lang+'.srt', 'Subs'), unsafe_allow_html=True)
            except Exception as e:
                st.error(
                    f"Sorry, there was a problem processing your Reference SRT./n {e}"
                )
                english_subs = None


            #if st.button('Download input as a text file'):
            #    tmp_download_link = download_link(lang+".srt", lang+".srt", 'Click here to download your text!')
            #    st.markdown(tmp_download_link, unsafe_allow_html=True)









#----------------------Formatting------------------------
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

#local_css("style.css")
#remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')



def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def get_table_download_link(df):
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download XLXS</a>' # decode b'abc' => abc



def get_table_download_link_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="extract.csv">Download csv file</a>'
    return href
