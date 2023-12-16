ref: https://developer.mozilla.org/en-US/docs/Web/API/Geolocation/getCurrentPosition
ref: https://www.cnblogs.com/Renyi-Fan/p/9223370.html

```
navigator.geolocation.getCurrentPosition(okfn, errfn);

position = ref: https://developer.mozilla.org/en-US/docs/Web/API/GeolocationPosition
position[attrs] = ref: https://developer.mozilla.org/en-US/docs/Web/API/GeolocationCoordinates
```

ref: https://developer.mozilla.org/en-US/docs/Web/API/USB
ref: https://stackoverflow.com/questions/50798704/webusb-api-navigator-usb-requestdevice

```
const filters = [{}];
  navigator.usb.requestDevice({
      filters: filters
    })
    .then(usbDevice => {
      console.log(usbDevice.manufacturerName, usbDevice.productName);
    })
    .catch(e => {
      console.log("There is no device. " + e);
    });
```
