using System.Collections.Generic;
using System.Text;

namespace LoLoX
{
    public class Json
    {
        object root;

        public Json()
        {
            root = null;
        }

        public Json(string json)
        {
            parse(json, 0, out root);
        }

        public static Json New(object root)
        {
            Json json = new Json();
            json.root = root;
            return json;
        }

        public Json Get(string path)
        {
            string[] parts = path.Split('.');
            object cur = root;
            for(int i = 0; i < parts.Length; i++)
            {
                string key = parts[i];
                if (cur is Dictionary<string, object>)
                {
                    Dictionary<string, object> obj = (Dictionary<string, object>)cur;
                    if (!obj.ContainsKey(key)) return null;
                    cur = obj[key];
                }
                else
                {
                    return null;
                }
            }
            return New(cur);
        }

        public double GetDouble()
        {
            if (root == null) return double.NaN;
            if (root is double) return (double)root;
            if (root is int) return (double)root;
            return double.NaN;
        }

        public int GetInt()
        {
            if (root == null) return 0;
            if (root is double) return (int)root;
            if (root is int) return (int)root;
            return 0;
        }

        public string GetString()
        {
            if (root == null) return null;
            if (root is string) return (string)root;
            if (root is double) return root.ToString();
            if (root is int) return root.ToString();
            return "[object]";
        }

        public Json GetArray()
        {
            if (root == null) return null;
            if (root is List<object>) return New(root);
            return null;
        }

        public int GetArrayLength()
        {
            if (root == null) return 0;
            if (root is List<object>) return ((List<object>)root).Count;
            return 0;
        }

        public Json GetArrayElement(int index)
        {
            if (root == null) return null;
            if (!(root is List<object>)) return null;
            List<object> L = (List<object>)root;
            if (index < 0 || index >= L.Count) return null;
            return New(L[index]);
        }

        public bool IsArray()
        {
            return root is List<object>;
        }

        public Json GetObject()
        {
            if (root == null) return null;
            if (root is Dictionary<string, object>) return New(root);
            return null;
        }

        public bool IsObject()
        {
            return root is Dictionary<string, object>;
        }

        public bool IsNull()
        {
            return root == null;
        }

        private int parse(string json, int st, out object output)
        {
            output = null;
            int cur = skipSpace(json, st), aux;
            if (cur >= json.Length) return -1;
            cur = parseVal(json, cur, out output);
            if (cur < 0)
            {
                char ch = json[st];
                if (ch == '{')
                {
                    // "key": <val>,
                    // "key": <val>}
                    Dictionary<string, object> obj = new Dictionary<string, object>();
                    cur = skipSpace(json, st+1);
                    if (cur >= json.Length) return -1;
                    do
                    {
                        aux = parseString(json, cur);
                        if (aux < 0)
                        {
                            if (json[cur] == '}') break; // e.g. { }
                            return -1;
                        }
                        string key = transformString(json.Substring(cur, aux - cur));
                        cur = skipSpace(json, aux);
                        if (cur >= json.Length) return -1;
                        if (json[cur] != ':') return -1;
                        cur = skipSpace(json, cur + 1);
                        if (cur >= json.Length) return -1;
                        object val;
                        cur = parse(json, cur, out val);
                        if (cur < 0) return -1;
                        obj[key] = val;
                        cur = skipSpace(json, cur);
                        if (cur >= json.Length) return -1;
                        if (json[cur] == ',') cur = skipSpace(json, cur + 1);
                    } while (true);
                    cur++; // move out of }
                    output = obj;
                    return cur;
                }
                else if (ch == '[')
                {
                    List<object> arr = new List<object>();
                    cur = skipSpace(json, st+1);
                    if (cur >= json.Length) return -1;
                    do
                    {
                        object val;
                        aux = parse(json, cur, out val);
                        if (aux < 0)
                        {
                            if (json[cur] == ']') break;
                            return -1;
                        }
                        arr.Add(val);
                        cur = skipSpace(json, aux);
                        if (cur >= json.Length) return -1;
                        if (json[cur] == ']') break;
                        if (json[cur] != ',') return -1;
                        cur++;
                    } while (true);
                    cur++; // move out of ]
                    output = arr;
                    return cur;
                }
                else
                {
                    output = null;
                    return -1;
                }
            }
            return cur;
        }

        private int skipSpace(string json, int st)
        {
            int ed = st;
            while (ed < json.Length)
            {
                char ch = json[ed];
                if (ch == ' ' || ch == '\r' || ch == '\n' || ch == '\t')
                {
                    ed++;
                    continue;
                }
                break;
            }
            return ed;
        }

        private int parseVal(string json, int st, out object obj)
        {
            int next = parseInteger(json, st);
            if (next > 0)
            {
                int pfed = parsePointAndFloat(json, next);
                if (pfed > 0)
                {
                    obj = double.Parse(json.Substring(st, pfed - st));
                    return pfed;
                }
                int sfed = parseScientificFloat(json, next);
                if (sfed > 0)
                {
                    obj = double.Parse(json.Substring(st, sfed - st));
                    return sfed;
                }
                obj = int.Parse(json.Substring(st, next - st));
                return next;
            }
            next = parseBoolean(json, st);
            if (next > 0)
            {
                obj = bool.Parse(json.Substring(st, next - st));
                return next;
            }
            next = parseNull(json, st);
            if (next > 0)
            {
                obj = null;
                return next;
            }
            next = parseString(json, st);
            if (next > 0)
            {
                obj = transformString(json.Substring(st, next - st));
                return next;
            }
            obj = null;
            return -1;
        }

        private int parseInteger(string txt, int st)
        {
            int ed = st;
            bool sign = false;
            if (txt[st] == '-')
            {
                sign = true;
                ed++;
            }
            do
            {
                char ch = txt[ed];
                if (ch < '0' || ch > '9')
                {
                    if (ed == st) return -1;
                    if (sign && ed == st + 1) return -1;
                    return ed;
                }
                ed++;
            } while (ed < txt.Length);
            return ed;
        }

        private int parseScientificFloat(string txt, int st)
        {
            if (txt[st] != 'e') return -1;
            int ed = st + 1;
            bool sign = false;
            if (txt[st] == '-' || txt[st] == '+')
            {
                sign = true;
                ed++;
            }
            do
            {
                char ch = txt[ed];
                if (ch < '0' || ch > '9')
                {
                    if (ed == st) return -1;
                    if (sign && ed == st + 2) return -1;
                    return ed;
                }
                ed++;
            } while (ed < txt.Length);
            return ed;
        }

        private int parsePointAndFloat(string txt, int st)
        {
            if (txt[st] != '.') return -1;
            int ed = st + 1;
            do
            {
                char ch = txt[ed];
                if (ch < '0' || ch > '9')
                {
                    if (ed == st) return -1;
                    return ed;
                }
                ed++;
            } while (ed < txt.Length);
            return ed;
        }

        private int parseString(string txt, int st)
        {
            if (txt[st] != '"') return -1;
            int ed = st + 1;
            do
            {
                char ch = txt[ed];
                if (ch == '\\')
                {
                    ed++;
                    if (ed >= txt.Length) return -1;
                    // skip \n \r \" ...
                }
                else if (ch == '"') return ed + 1;
                ed++;
            } while (ed < txt.Length);
            return ed;
        }

        private int parseBoolean(string txt, int st)
        {
            if (txt.Substring(st, 4) == "true") return st + 4;
            if (txt.Substring(st, 5) == "false") return st + 5;
            return -1;
        }

        private int parseNull(string txt, int st)
        {
            if (txt.Substring(st, 4) == "null") return st + 4;
            return -1;
        }

        private string transformString(string jsonString)
        {
            string[] parts = jsonString.Substring(1, jsonString.Length - 2).Split('\\');
            for (int i = 1; i < parts.Length; i ++)
            {
                parts[i] = transformString0(parts[i]);
            }
            return string.Join("", parts);
        }

        private string transformString0(string cuttedJsonString)
        {
            if (cuttedJsonString.Length == 0) return cuttedJsonString;
            char ch = cuttedJsonString[0];
            switch (ch)
            {
                case 'n':
                    return string.Format("\n{0}", cuttedJsonString.Substring(1));
                case 'r':
                    return string.Format("\r{0}", cuttedJsonString.Substring(1));
                case 'x':
                    {
                        int a = cuttedJsonString[1] - '0', b = cuttedJsonString[2] - '0';
                        if (a > 9) a -= -7; // a = char - ('0' + 17 -> 'a') + 10
                        if (b > 9) b -= -7;
                        byte c = (byte)(a * 16 + b);
                        return string.Format("{0}{1}", (char)c, cuttedJsonString.Substring(3));
                    }
                case 'u':
                    {
                        int a = cuttedJsonString[1] - '0', b = cuttedJsonString[2] - '0';
                        int c = cuttedJsonString[3] - '0', d = cuttedJsonString[4] - '0';
                        if (a > 9) a -= -7; // a = char - ('0' + 17 -> 'a') + 10
                        if (b > 9) b -= -7;
                        if (c > 9) c -= -7;
                        if (d > 9) d -= -7;
                        byte clow = (byte)(a * 16 + b), chigh = (byte)(c * 16 + d);
                        return string.Format("{0}{1}", Encoding.Unicode.GetString(new byte[] { chigh, clow }), cuttedJsonString.Substring(5));
                    }
            }
            return cuttedJsonString.Substring(1);
        }
    }
}
