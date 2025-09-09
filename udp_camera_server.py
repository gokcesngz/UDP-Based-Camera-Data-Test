import time
import cv2
import socket
import struct
import numpy as np

# UDP server ayarları
CAMERA_INDEX = 0
WIDTH = 320
HEIGHT = 240
REPORT_INTERVAL = 2.0  # saniye

# UDP ayarları
UDP_IP = "127.0.0.1"  # Localhost
UDP_PORT = 5005       # UDP port numarası
BUFFER_SIZE = 65536   # Buffer boyutu

def main() -> None:
    
    # UDP socket oluştur
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Buffer boyutlarını ayarla
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)  # İsteğe bağlı
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)  # ÖNEMLİ
    
    # Kamerayı aç
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    
    # Çözünürlük ayarları
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    
    # Performans metrikleri
    t0 = time.time()
    frames = 0
    total_latency = 0
    total_udp_time = 0
    total_bytes_sent = 0

    try:
        while True:
            # Frame işleme başlangıcı
            frame_start = time.time()
            
            # Kameradan frame al
            ok, frame = cap.read()
            if not ok:
                continue

            frames += 1

            # Frame'i JPEG'e çevir (UDP için sıkıştır)
            encode_start = time.time()
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]  # %80 kalite
            result, encoded_img = cv2.imencode('.jpg', frame, encode_param)
            encode_time = (time.time() - encode_start) * 1000
            
            if not result:
                continue
            
            # UDP ile gönder
            udp_start = time.time()
            try:
                # Frame boyutunu gönder (4 byte)
                frame_size = len(encoded_img)
                sock.sendto(struct.pack("!I", frame_size), (UDP_IP, UDP_PORT))
                
                # Frame verisini gönder
                sock.sendto(encoded_img.tobytes(), (UDP_IP, UDP_PORT))
                
                udp_time = (time.time() - udp_start) * 1000
                total_udp_time += udp_time
                total_bytes_sent += frame_size
                
            except Exception as e:
                print(f" UDP gönderme hatası: {e}")
                continue

            # Frame'i göster
            cv2.imshow("UDP Server - Kamera", frame)
            
            # Frame işleme bitişi
            frame_end = time.time()
            
            # Bu frame'in latency'sini hesapla (milisaniye cinsinden)
            frame_latency = (frame_end - frame_start) * 1000
            total_latency += frame_latency

            # Her 2 saniyede bir rapor ver
            if time.time() - t0 >= REPORT_INTERVAL:
                dt = time.time() - t0
                fps = frames / dt
                avg_latency = total_latency / frames
                avg_udp_time = total_udp_time / frames
                avg_bytes_per_frame = total_bytes_sent / frames
                bandwidth_mbps = (total_bytes_sent * 8) / (dt * 1000000)  # Mbps
                
                h, w = frame.shape[:2]
                print("UDP SERVER PERFORMANSI:")
                print(f"  Gönderilen FPS: {fps:.1f}")
                print(f"  Çözünürlük: {w}x{h}")
                print(f"  Ortalama Latency: {avg_latency:.1f}ms")
                print(f"  JPEG Sıkıştırma Süresi: {encode_time:.1f}ms")
                print(f"  UDP Gönderme Süresi: {avg_udp_time:.1f}ms")
                print(f"  Frame Boyutu: {avg_bytes_per_frame:.0f} bytes")
                print(f"  Bant Genişliği: {bandwidth_mbps:.2f} Mbps")
                print(f"  Hedef: {UDP_IP}:{UDP_PORT}")
                print("-" * 60)
                
                # Sayaçları sıfırla
                t0 = time.time()
                frames = 0
                total_latency = 0
                total_udp_time = 0
                total_bytes_sent = 0

            # 'q' tuşuna basılırsa çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n UDP server durduruldu!")
    finally:
        cap.release()
        sock.close()
        cv2.destroyAllWindows()
        print(" Kaynaklar temizlendi!")

if __name__ == "__main__":
    main()
