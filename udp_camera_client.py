import time
import cv2
import socket
import struct
import numpy as np

# UDP client ayarları
UDP_IP = "127.0.0.1"  # Localhost
UDP_PORT = 5005       # UDP port numarası (server ile aynı)
BUFFER_SIZE = 65536   # Buffer boyutu

def main() -> None:
    
    # UDP socket oluştur
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(1.0)  # 1 saniye timeout

    # Performans metrikleri
    t0 = time.time()
    frames_received = 0
    total_receive_time = 0
    total_bytes_received = 0
    last_frame_time = time.time()

    try:
        while True:
            try:
                # Frame boyutunu al
                data, addr = sock.recvfrom(4)  # 4 byte (frame size)
                frame_size = struct.unpack("!I", data)[0]
                
                # Frame verisini al
                frame_data, addr = sock.recvfrom(frame_size)
                
                receive_time = time.time()
                total_receive_time += (receive_time - last_frame_time) * 1000
                total_bytes_received += frame_size
                frames_received += 1
                
                # Frame'i decode et
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Frame'i göster
                    cv2.imshow("UDP Client - Kamera", frame)
                    
                    # Performans raporu (her 2 saniyede)
                    if time.time() - t0 >= 2.0:
                        dt = time.time() - t0
                        fps = frames_received / dt
                        avg_receive_time = total_receive_time / frames_received
                        avg_bytes_per_frame = total_bytes_received / frames_received
                        bandwidth_mbps = (total_bytes_received * 8) / (dt * 1000000)
                        
                        h, w = frame.shape[:2]
                        print("UDP CLIENT PERFORMANSI:")
                        print(f"  Alınan FPS: {fps:.1f}")
                        print(f"  Çözünürlük: {w}x{h}")
                        print(f"  Ortalama Alım Süresi: {avg_receive_time:.1f}ms")
                        print(f"  Frame Boyutu: {avg_bytes_per_frame:.0f} bytes")
                        print(f"  Bant Genişliği: {bandwidth_mbps:.2f} Mbps")
                        print(f"  Gönderen: {addr[0]}:{addr[1]}")
                        print("-" * 60)
                        
                        # Sayaçları sıfırla
                        t0 = time.time()
                        frames_received = 0
                        total_receive_time = 0
                        total_bytes_received = 0
                
                last_frame_time = receive_time
                
            except socket.timeout:
                # Timeout - veri gelmedi
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
                
            except Exception as e:
                print(f" Alım hatası: {e}")
                continue

            # 'q' tuşuna basılırsa çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n UDP client durduruldu!")
    finally:
        sock.close()
        cv2.destroyAllWindows()
        print(" Kaynaklar temizlendi!")

if __name__ == "__main__":
    main()
