#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#include "slip.h"
#include "wrap.h"

static Slirp* slirp = NULL;
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

    slirp = slirp_init_with_config();

    fprintf(stderr, "Slirp program started. Reading from stdin and writing to stderr.\n");
    fprintf(stderr, "Press Ctrl+C or send SIGTERM to exit gracefully.\n\n");
    
    // Allocate initial fd mapping array
    PollData poll_data = {0};
    poll_data.fd_capacity = 16;
    poll_data.fd_map = malloc(poll_data.fd_capacity * sizeof(FdMapping));

    // Main loop: read from stdin and write to stderr
    while (keep_running) {
        fd_set rfds, wfds, xfds;
        struct timeval tv;
        int timeout = 60000;

        FD_ZERO(&rfds);
        FD_ZERO(&wfds);
        FD_ZERO(&xfds);
        
        // Add SLIRP file descriptors to select
        poll_data.rfds = &rfds;
        poll_data.wfds = &wfds;
        poll_data.xfds = &xfds;
        poll_data.max_fd = -1;
        poll_data.fd_count = 0;
        slirp_pollfds_fill(slirp, &timeout, add_poll_cb, &poll_data);
        
        // Wait for events
        int ret = select(poll_data.max_fd + 1, &rfds, &wfds, &xfds, &tv);
        
        if (ret < 0) {
            if (errno != EINTR) {
                perror("select");
                break;
            }
        } else if (ret > 0) {
            // Process SLIRP events
            slirp_pollfds_poll(slirp, (ret < 0), get_revents_cb, &poll_data);
        }
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
            outlen = slip_decode(buffer, bytes_read, outbuf);
            size_t tmplen = load_ethernet(outbuf, outlen, tmpbuf); // if packet is too large, may out of bound
            //dump_buf(buffer, outlen);
            dump_buf(tmpbuf, tmplen);
            slirp_input(slirp, tmpbuf, tmplen);
            usleep(1000);
        }
    }

    if (slirp) {
       // Cleanup
       slirp_cleanup(slirp);
    }
    
    fprintf(stderr, "\nProgram terminated.\n");
    return 0;
}
