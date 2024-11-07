from flask import Flask, render_template, Response
from flask_cors import CORS
import psycopg2
import logging
import time

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL 데이터베이스 연결 설정
def get_db_connection():
    logger.info("Connecting to PostgreSQL database...")
    conn = psycopg2.connect(
        host="ohiopostgre.c782uy2a401d.us-east-2.rds.amazonaws.com",
        port="5432",
        database="postgre_test",        # 실제 데이터베이스 이름으로 변경
        user="ohiopostgre",
        password="ohio1234"
    )
    logger.info("Successfully connected to the database.")
    return conn

# SSE를 통해 0.5초 간격으로 데이터를 실시간 전송
@app.route('/stream')
def stream_data():
    def generate():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT level FROM "mysql-busan";')

        for row in cursor:
            level_data = row[0]
            logger.info(f"Sending data: {level_data}")  # 데이터 전송 로그
            yield f"data: {level_data}\n\n"  # SSE 형식으로 데이터 전송
            time.sleep(0.5)  # 0.5초 대기

        cursor.close()
        conn.close()

    return Response(generate(), mimetype='text/event-stream')

# HTML 렌더링을 위한 라우트
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True)
