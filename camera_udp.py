import time

import cv2


# Basit ayarlar (ilk adım): sadece kameradan veri al, GUI yok
CAMERA_INDEX = 0
WIDTH = 320
HEIGHT = 240
REPORT_INTERVAL = 2.0  # saniye


def main() -> None:
    # Kamerayı aç
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)  # Windows'ta daha stabil
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    t0 = time.time()
    frames = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue  # Kare alınamazsa denemeye devam et

            frames += 1

            cv2.imshow("Kamera", frame)

            # Periyodik FPS raporu
            if time.time() - t0 >= REPORT_INTERVAL:
                dt = time.time() - t0
                fps = frames / dt
                h, w = frame.shape[:2]
                print(f"CAM | fps:{fps:.1f} res:{w}x{h}")
                t0 = time.time()
                frames = 0

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()


if __name__ == "__main__":
    main()


