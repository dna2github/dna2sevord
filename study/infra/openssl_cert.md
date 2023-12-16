# create cert with extensions via openssl

```
[ req ]
distinguished_name  = req_distinguished_name
req_extetions = v3_req

[req_distinguished_name]
countryName = Country Name (2 letter code)
countryName_default = XX
stateOrProvinceName = State or Province Name (full name)
stateOrProvinceName_default = Province
localityName = Locality Name (eg, city)
localityName_default = City
organizationalUnitName  = Organizational Unit Name (eg, section)
organizationalUnitName_default  = Company
commonName = hostName
commonName_max  = 64

[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.hello-world.com
DNS.2 = *.foo-bar.com
IP.1 = 127.0.0.1
```

```
openssl req -new -nodes -x509 -keyout ca.key -newkey rsa:4096 -out ca.crt -config ssl.conf -extensions v3_req
```


## windows pfx and signtool
```
openssl pkcs12 -export -in linux_cert+ca.pem -inkey privateky.key -out output.pfx
SignTool sign /f MyCert.pfx /p MyPassword /t http://timestamp.digicert.com /n "companyname" my.exe
```
