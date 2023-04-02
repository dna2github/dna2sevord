```
    public static class BitmapUtil
    {
        public static Bitmap Crop(Image src, Rectangle bounds)
        {
            Bitmap p = new Bitmap(bounds.Width, bounds.Height);
            Rectangle r = new Rectangle(-bounds.X, -bounds.Y, bounds.X * 2 + bounds.Width, bounds.Y * 2 + bounds.Height);
            Graphics g = Graphics.FromImage(p);
            g.DrawImageUnscaledAndClipped(src, r);
            g.Dispose();
            return p;
        }
        public static Bitmap CropAndStretch(Image src, Rectangle bounds, int sw, int sh)
        {
            if (src == null) return null;
            Bitmap p = new Bitmap(sw, sh);
            Graphics g = Graphics.FromImage(p);
            g.DrawImage(src, new Rectangle(0, 0, sw, sh), bounds.X, bounds.Y, bounds.Width, bounds.Height, GraphicsUnit.Pixel);
            g.Dispose();
            return p;
        }

        public static byte[] GetBitmapRaw(Bitmap src)
        {
            BitmapData x;
            x = src.LockBits(new Rectangle(0, 0, src.Width, src.Height), ImageLockMode.ReadOnly, src.PixelFormat);
            IntPtr xraw = x.Scan0;
            int len = src.Width * src.Height * 4;
            byte[] raw = new byte[len];
            System.Runtime.InteropServices.Marshal.Copy(xraw, raw, 0, len);
            src.UnlockBits(x);
            return raw;
        }

        public static double DiffBitmapRaw(byte[] a, byte[] b)
        {
            if (a == null || b == null || a.Length != b.Length) return Double.PositiveInfinity;
            byte[] r = new byte[a.Length];
            for (int i = 0; i < r.Length; i++)
            {
                if (i % 4 == 3) continue;
                byte va = a[i], vb = b[i];
                if (va > vb)
                {
                    r[i] = (byte)(va - vb);
                }
                else
                {
                    r[i] = (byte)(vb - va);
                }
            }
            return AggDiffBitmapRaw(r);
        }

        private static double AggDiffBitmapRaw(byte[] diff)
        {
            if (diff == null || diff.Length == 0) return double.PositiveInfinity;
            double sum = 0.0;
            for (int i = 0; i < diff.Length; i++)
            {
                byte v = diff[i];
                if (v == 0) continue;
                sum += v / 255.0;
            }
            return sum;
        }

        public static double CosSqBitmapRaw(byte[] a, byte[] b)
        {
            if (a == null || b == null || a.Length != b.Length) return 1.0;
            double mab = 0.0, ma = 0.0, mb = 0.0;
            for (int i = 0; i < a.Length; i++)
            {
                double va = a[i] / 255.0, vb = b[i] / 255.0;
                mab += va * vb;
                ma += va * va;
                mb += vb * vb;
            }
            return mab / ma * mab / mb;
        }

        public static int[] GetBitmapHistogram(byte[] raw)
        {
            int[] r = new int[3 * 257];
            for (int i = 0; i < raw.Length; i += 4)
            {
                r[raw[i]]++;
                r[257 + raw[i + 1]]++;
                r[514 + raw[i + 2]]++;
            }
            return r;
        }

        public static double CosSqBitmapHistogram(int[] a, int[] b)
        {
            if (a == null || b == null || a.Length != b.Length) return 1.0;
            double mab = 0.0, ma = 0.0, mb = 0.0;
            for (int i = 0; i < a.Length; i++)
            {
                int va = a[i], vb = b[i];
                mab += va * vb;
                ma += va * va;
                mb += vb * vb;
            }
            return mab / ma * mab / mb;
        }

        private static double cosSq(int[] a, int[] b, int st, int ed)
        {
            double mab = 0.0, ma = 0.0, mb = 0.0;
            for (int i = st; i < ed; i++)
            {
                int va = a[i], vb = b[i];
                mab += va * vb;
                ma += va * va;
                mb += vb * vb;
            }
            return mab / ma * mab / mb;
        }
        public static double CosSqx3BitmapHistogram(int[] a, int[] b)
        {
            if (a == null || b == null || a.Length != b.Length) return 1.0;
            double rs = Math.Log(1.0 / cosSq(a, b, 0, 256));
            double gs = Math.Log(1.0 / cosSq(a, b, 257, 513));
            double bs = Math.Log(1.0 / cosSq(a, b, 514, a.Length - 1));
            return (rs + gs + bs) / 3.0;
        }

        public static Bitmap ToBitmap(byte[] src, int w, int h)
        {
            if (w == 0 || h == 0) return null;
            int len = w * h * 4;
            byte[] bitmapraw = new byte[len];
            Array.Copy(src, bitmapraw, len);
            for (int i = 3; i < src.Length; i += 4)
            {
                bitmapraw[i] = 255;
            }
            Bitmap bmp = new Bitmap(w, h);
            BitmapData x;
            x = bmp.LockBits(new Rectangle(0, 0, bmp.Width, bmp.Height), ImageLockMode.WriteOnly, bmp.PixelFormat);
            IntPtr xraw = x.Scan0;
            System.Runtime.InteropServices.Marshal.Copy(bitmapraw, 0, xraw, len);
            bmp.UnlockBits(x);
            return bmp;
        }

        public static Bitmap ToGrayscaleBitmap(Bitmap original)
        {
            if (original == null) return null;
            Bitmap newBmp = new Bitmap(original.Width, original.Height);
            Graphics g = Graphics.FromImage(newBmp);
            ColorMatrix colorMatrix = new ColorMatrix(
               new float[][]
               {
                   new float[] {.3f, .3f, .3f, 0, 0},
                   new float[] {.59f, .59f, .59f, 0, 0},
                   new float[] {.11f, .11f, .11f, 0, 0},
                   new float[] {0, 0, 0, 0.2f, 0},
                   new float[] {0, 0, 0, 0, 1}
               });
            ImageAttributes img = new ImageAttributes();
            img.SetColorMatrix(colorMatrix);
            g.DrawImage(original, new Rectangle(0, 0, original.Width, original.Height), 0, 0, original.Width, original.Height, GraphicsUnit.Pixel, img);
            g.Dispose();
            return newBmp;
        }

        public static Size GetDPI()
        {
            IntPtr desktop = NativeMethods.GetDC(IntPtr.Zero);
            int dpiX = NativeMethods.GetDeviceCaps(desktop, 88 /* LOGPIXELSX */);
            int dpiY = NativeMethods.GetDeviceCaps(desktop, 90 /* LOGPIXELSY */);
            NativeMethods.ReleaseDC(IntPtr.Zero, desktop);
            return new Size(dpiX, dpiY);
        }

        public static Rectangle GetScreenSize()
        {
            IntPtr desktopHwnd = NativeMethods.GetDesktopWindow();
            Rectangle rect = Screen.FromHandle(desktopHwnd).Bounds;
            IntPtr desktop = NativeMethods.GetDC(desktopHwnd);
            NativeMethods.ReleaseDC(desktopHwnd, desktop);
            return rect;
        }

        public static Rectangle GetActiveWindowSize()
        {
            IntPtr win = NativeMethods.GetForegroundWindow();
            Rectangle rect;
            if (win == IntPtr.Zero) return new Rectangle(0, 0, 0, 0);
            NativeMethods.GetWindowRect(win, out rect);
            rect.Width = rect.Width - rect.Left;
            rect.Height = rect.Height - rect.Top;
            if (rect.Width <= 0 || rect.Height <= 0) return new Rectangle(0, 0, 0, 0);
            return rect;
        }

        public static Bitmap CaptureScreen()
        {
            Rectangle rect = GetScreenSize();
            using (Bitmap bitmap = new Bitmap(rect.Width, rect.Height))
            {
                using (Graphics g = Graphics.FromImage(bitmap))
                {
                    g.CopyFromScreen(new Point(0, 0), Point.Empty, rect.Size);
                }
                return bitmap.Clone(new Rectangle(0, 0, bitmap.Width, bitmap.Height), PixelFormat.Format32bppArgb);
            }
        }
        public static Bitmap CaptureActiveWindow()
        {
            IntPtr win = NativeMethods.GetForegroundWindow();
            Rectangle rect;
            if (win == IntPtr.Zero) return null;
            NativeMethods.GetWindowRect(win, out rect);
            rect.Width = rect.Width - rect.Left;
            rect.Height = rect.Height - rect.Top;
            if (rect.Width <= 0 || rect.Height <= 0) return null;
            using (Bitmap bitmap = new Bitmap(rect.Width, rect.Height))
            {
                using (Graphics g = Graphics.FromImage(bitmap))
                {
                    Size winsize = new Size(rect.Width, rect.Height);
                    g.CopyFromScreen(new Point(rect.Left, rect.Top), Point.Empty, winsize);
                }
                return bitmap.Clone(new Rectangle(0, 0, bitmap.Width, bitmap.Height), PixelFormat.Format32bppArgb);
            }
        }

        private delegate int SetProcessDpiAwareness(int mode);
        public static void EnableDpiAwareness()
        {
            // skip this procedure if Windows version is below
            // Shcore.dll#SetProcessDpiAwareness [min] Windows 8.1 / Windows Server 2012 R2
            IntPtr shcoreDll = NativeMethods.LoadLibrary(@"Shcore.dll");
            if (shcoreDll != IntPtr.Zero)
            {
                IntPtr ptrSetProcessDpiAwareness = NativeMethods.GetProcAddress(shcoreDll, "SetProcessDpiAwareness");
                if (ptrSetProcessDpiAwareness != IntPtr.Zero)
                {
                    SetProcessDpiAwareness fnSetProcessDpiAwareness = (SetProcessDpiAwareness)System.Runtime.InteropServices.Marshal.GetDelegateForFunctionPointer(ptrSetProcessDpiAwareness, typeof(SetProcessDpiAwareness));
                    fnSetProcessDpiAwareness(/* DPI_AWARENESS_SYSTEM_AWARE */ 1);
                }
                NativeMethods.FreeLibrary(shcoreDll);
            }
            Size size = GetDPI();
            Stat.CaptureStat.dpiX = size.Width;
            Stat.CaptureStat.dpiY = size.Height;
            Stat.CaptureStat.scaleX = size.Width / 96.0;
            Stat.CaptureStat.scaleY = size.Height / 96.0;
        }

        public static string CaptureActiveWindowTitle()
        {
            IntPtr win = NativeMethods.GetForegroundWindow();
            if (win == IntPtr.Zero) return null;
            StringBuilder name = new StringBuilder(1024);
            NativeMethods.GetWindowText(win, name, name.Capacity);
            return name.ToString();
        }
    }
```
