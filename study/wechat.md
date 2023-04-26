## backend may use

```js
/*
 * ref: https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/Wechat_webpage_authorization.html
 * ref: https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html
 * https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
 * appid, secret, code, grant_type
 * access_token, expires_in, refresh_token, openid, scope
 * errcode, errmsg | {"errcode":40029,"errmsg":"invalid code"}
 *
 * https://api.weixin.qq.com/sns/oauth2/refresh_token?appid=APPID&grant_type=refresh_token&refresh_token=REFRESH_TOKEN
 * appid, grant_type, refresh_token
 * access_token, expires_in, refresh_token, openid, scope
 * errcode, errmsg | {"errcode":40029,"errmsg":"invalid code"}
 *
 * https://api.weixin.qq.com/sns/userinfo?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN
 * access_token, openid, lang
 * openid, nickname, sex, province, city, country, headimgurl, privilege, unionid
 * {"errcode":40003,"errmsg":" invalid openid "}
*/
function getWeChatAccessToken(wechatAppId, wechatSecret, code) {
   return new Promise((r) => {
      const req = i_https.request({
         hostname: 'api.weixin.qq.com',
         port: 443,
         path: `/sns/oauth2/access_token?appid=${wechatAppId}&secret=${wechatSecret}&code=${code}&grant_type=authorization_code`,
         method: 'GET',
      }, async (res) => {
         if (~~(res.statusCode/100) !== 2) {
            return r(null);
         }
         try {
            const tokenObj = await getResponseData(res);
            if (!tokenObj) return r(null);
            if (tokenObj.errcode) return r(null);
            return r(tokenObj);
         } catch(err) {
            r(null);
         }
      });
      req.on('error', (err) => {
         r(null);
      });
      req.end();
   });
}

function getWeChatUserInfo(wechatAccessToken, wechatOpenId) {
   return new Promise((r) => {
      const req = i_https.request({
         hostname: 'api.weixin.qq.com',
         port: 443,
         path: `/sns/userinfo?access_token=${wechatAccessToken}&openid=${wechatOpenId}&lang=zh_CN`,
         method: 'GET',
      }, async (res) => {
         if (~~(res.statusCode/100) !== 2) {
            return r(null);
         }
         try {
            const userObj = await getResponseData(res);
            if (!userObj) return r(null);
            if (userObj.errcode) return r(null);
            return r(userObj);
         } catch(err) {
            r(null);
         }
      });
      req.on('error', (err) => {
         r(null);
      });
      req.end();
   });
}

```

## frontend may use

```js
function appendRedirect() {
   return urlObj.redirect ? ('?redirect=' + encodeURIComponent(urlObj.redirect)) : '';
}

function goWechatOneClickLogin() {
   var url = 'https://open.weixin.qq.com/connect/oauth2/authorize';
   url += '?appid=' + envObj.wechat.oneclick;
   url += '&redirect_uri=' + encodeURIComponent(envObj.wechat.oneclickUrl + appendRedirect());
   url += '&response_type=code&scope=snsapi_userinfo&state=wechat#wechat_redirect';
   window.location = url;
}

function goWechatQrLogin() {
   var url = 'https://open.weixin.qq.com/connect/qrconnect';
   url += '?appid=' + envObj.wechat.qr;
   url += '&redirect_uri=' + encodeURIComponent(envObj.wechat.qrUrl + appendRedirect());
   url += '&response_type=code&scope=snsapi_login&state=web#wechat_redirect';
   window.location = url;
}

authCheck().then(function () {
  goTarget();
}, function () {
  if (utils.isWeChatBrowser()) { // window.navigator.userAgent.toLowerCase().match(/MicroMessenger/i) == 'micromessenger'
     goWechatOneClickLogin();
  } else {
     goWechatQrLogin();
  }
});
```
