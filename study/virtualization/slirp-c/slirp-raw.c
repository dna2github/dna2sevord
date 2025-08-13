#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#include "slip.h"
#include "response.h"

volatile sig_atomic_t keep_running = 1;

void signal_handler(int signum) {
    switch(signum) {
        case SIGINT:
            fprintf(stderr, "\nReceived SIGINT (Ctrl+C). Exiting gracefully...\n");
            break;
        case SIGTERM:
            fprintf(stderr, "\nReceived SIGTERM. Exiting gracefully...\n");
            break;
        case SIGHUP:
            fprintf(stderr, "\nReceived SIGHUP. Exiting gracefully...\n");
            break;
        default:
            fprintf(stderr, "\nReceived signal %d. Exiting gracefully...\n", signum);
    }
    keep_running = 0;
}

int main() {
    unsigned char buffer[1024 * 1024];
    unsigned char tmpbuf[1024 * 1024];
    unsigned char outbuf[2 * 1024 * 1024 + 2];
    ssize_t bytes_read, outlen;
    
    // Set up signal handlers
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    
    // Handle common termination signals
    if (sigaction(SIGINT, &sa, NULL) == -1) {
        perror("Error setting SIGINT handler");
        exit(1);
    }
    if (sigaction(SIGTERM, &sa, NULL) == -1) {
        perror("Error setting SIGTERM handler");
        exit(1);
    }
    if (sigaction(SIGHUP, &sa, NULL) == -1) {
        perror("Error setting SIGHUP handler");
        exit(1);
    }
    
    // Ignore SIGPIPE to handle broken pipes gracefully
    signal(SIGPIPE, SIG_IGN);

    fprintf(stderr, "Slirp program started. Reading from stdin and writing to stderr.\n");
    fprintf(stderr, "Press Ctrl+C or send SIGTERM to exit gracefully.\n\n");

    // Main loop: read from stdin and write to stderr
    while (keep_running) {
        bytes_read = read(STDIN_FILENO, buffer, sizeof(buffer));
        
        if (bytes_read == -1) {
            if (errno == EINTR) {
                // Interrupted by signal, check if we should continue
                continue;
            } else {
                perror("Error reading from stdin");
                break;
            }
        } else if (bytes_read == 0) {
            // EOF reached
            fprintf(stderr, "\nEOF reached on stdin. Exiting.\n");
            break;
        } else {
            // Write to stderr
            /*
            ssize_t bytes_written = 0;
            while (bytes_written < bytes_read && keep_running) {
                ssize_t result = write(STDERR_FILENO, buffer + bytes_written, 
                                     bytes_read - bytes_written);
                if (result == -1) {
                    if (errno == EINTR) {
                        continue;
                    } else {
                        perror("Error writing to stderr");
                        keep_running = 0;
                        break;
                    }
                }
                bytes_written += result;
            }
            */
            outlen = slip_decode(buffer, bytes_read, outbuf);
            dump_buf(outbuf, outlen);
            int reslen = 0;
            if (parse_and_respond(outbuf, outlen, tmpbuf, &reslen)) {
               fprintf(stderr, "parse and respond error ...\n");
               continue;
            }
            outlen = slip_encode(tmpbuf, reslen, outbuf);
            dump_buf(outbuf, outlen);
            dump_raw(outbuf, outlen);
        }
    }

    fprintf(stderr, "\nProgram terminated.\n");
    return 0;
}
