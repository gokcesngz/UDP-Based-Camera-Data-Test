import time
import cv2

# Basit ayarlar
CAMERA_INDEX = 0
WIDTH = 320
HEIGHT = 240
REPORT_INTERVAL = 2.0  # saniye

def main() -> None:
    # Kamerayı aç
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    
    
    # Çözünürlük ayarları (320x240 korunuyor)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    # Zaman ölçümü için değişkenler
    t0 = time.time()  # Başlangıç zamanı
    frames = 0        # Frame sayacı
    total_latency = 0 # Toplam latency

    try:
        while True:
            # Frame işleme başlangıcı
            frame_start = time.time()
            
            # Kameradan frame al
            ok, frame = cap.read()
            if not ok:
                continue

            frames += 1

            # Frame'i göster (her frame'de göster - en uygun)
            cv2.imshow("Kamera", frame)
            
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
                
                h, w = frame.shape[:2]
                print(f"FPS: {fps:.1f} | Çözünürlük: {w}x{h} | Ortalama Latency: {avg_latency:.1f}ms")
                
                # Sayaçları sıfırla
                t0 = time.time()
                frames = 0
                total_latency = 0

            # 'q' tuşuna basılırsa çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()

if __name__ == "__main__":
    main()