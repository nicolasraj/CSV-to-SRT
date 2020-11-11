FROM python:3.7
EXPOSE 8501
WORKDIR /app
RUN pip3 install pandas
RUN pip3 install pysrt
RUN pip3 install streamlit
COPY . .
CMD streamlit run Translation.py --server.port $PORT
