# Spring Boot

```
spring init --dependencies=web,thymeleaf --build=maven MyApplication.zip
unzip MyApplication.zip
...
mvn clean compile package
```

```
# src/java/resources/application.properties
#spring.thymeleaf.cache=false
#spring.thymeleaf.enabled=true
#spring.thymeleaf.prefix=classpath:/templates/
#spring.thymeleaf.suffix=.html

spring.application.name=HelloWorld
server.servlet.context-path=/springboot
```

```
# src/main/java/com/example/MyApplication/DemoApplication.java
package com.example.MyApplication;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class DemoApplication {

    @GetMapping("/hello")
    public String hello(@RequestParam(value = "name", defaultValue = "SpringBoot") String name) {
        return String.format("Hello %s!", name);
    }

        public static void main(String[] args) {
                SpringApplication.run(DemoApplication.class, args);
        }

}
```

```
@SpringBootApplication
@Mapper (mybatis)
@Autowired
@Service
@Bean
@Component
@Configure
@CrossOrigin
extends HandlerInterceptor -> preHandler, posthandler, afterCompletion
extends WebMvcConfigurerAdapter -> addInterceptor
implements Filter -> init, doFilter
@ComponentScan
@Controller
@RestController
@GetMapping
@RequestMapping
@RequestParam
@PathVariable
@RequestBody
@ControllerAdvice
@ExceptionHandler
@EnableScheduling
@Scheduled
@EnableSwagger2
@SpringBootTest
@Profile
```
