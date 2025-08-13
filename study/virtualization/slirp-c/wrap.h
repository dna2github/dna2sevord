#ifndef _WRAP_H_
#define _WRAP_H_
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <libslirp.h>
#include <time.h>

#include "slip.h"

int unload_ethernet(unsigned char* buf, unsigned int len, unsigned char* out, unsigned int* protocol) {
   for (int i = 14; i < len; i++) {
      *out = *buf;
      out ++;
      buf ++;
   }
   if (protocol) {
      // 0x0800 IP, 0x0806 ARP
      *protocol = buf[12] << 8 | buf[13];
   }
   return len - 14;
}

int load_ethernet(unsigned char* buf, unsigned int len, unsigned char* out) {
   *out = '\x00'; out++;
   *out = '\x00'; out++;
   *out = '\x00'; out++;
   *out = '\x00'; out++;
   *out = '\x00'; out++;
   *out = '\x00'; out++;
   *out = '\x54'; out++;
   *out = '\x52'; out++;
   *out = '\x0a'; out++;
   *out = '\x00'; out++;
   *out = '\x02'; out++;
   *out = '\x0f'; out++;
   *out = '\x08'; out++;
   *out = '\x00'; out++;
   for (int i = 0; i < len; i++) {
      *out = *buf;
      out ++;
      buf ++;
   }
   return len + 14;
}

// Structure to track file descriptors and their indices
typedef struct {
    int fd;
    int idx;
} FdMapping;

// Structure to hold select() sets and fd mappings
typedef struct {
    fd_set *rfds;
    fd_set *wfds;
    fd_set *xfds;
    int max_fd;
    FdMapping *fd_map;
    int fd_count;
    int fd_capacity;
} PollData;

// Updated add_poll_cb that tracks fd indices
static int add_poll_cb(int fd, int events, void *opaque) {
    PollData *poll_data = (PollData *)opaque;
    
    // Update the maximum file descriptor number
    if (fd > poll_data->max_fd) {
        poll_data->max_fd = fd;
    }
    
    // Add fd to appropriate sets based on requested events
    if (events & SLIRP_POLL_IN) {
        FD_SET(fd, poll_data->rfds);
    }
    if (events & SLIRP_POLL_OUT) {
        FD_SET(fd, poll_data->wfds);
    }
    if (events & SLIRP_POLL_PRI) {
        FD_SET(fd, poll_data->xfds);
    }
    
    // Store fd mapping
    if (poll_data->fd_count >= poll_data->fd_capacity) {
        poll_data->fd_capacity = poll_data->fd_capacity ? poll_data->fd_capacity * 2 : 16;
        poll_data->fd_map = realloc(poll_data->fd_map, 
                                    poll_data->fd_capacity * sizeof(FdMapping));
    }
    
    int idx = poll_data->fd_count;
    poll_data->fd_map[idx].fd = fd;
    poll_data->fd_map[idx].idx = idx;
    poll_data->fd_count++;
    
    return idx;  // Return the index, not the fd
}

// Callback to get events that occurred on a file descriptor
static int get_revents_cb(int idx, void *opaque) {
    PollData *poll_data = (PollData *)opaque;
    int revents = 0;
    
    if (idx < 0 || idx >= poll_data->fd_count) {
        return 0;
    }
    
    int fd = poll_data->fd_map[idx].fd;
    
    if (FD_ISSET(fd, poll_data->rfds)) {
        revents |= SLIRP_POLL_IN;
    }
    if (FD_ISSET(fd, poll_data->wfds)) {
        revents |= SLIRP_POLL_OUT;
    }
    if (FD_ISSET(fd, poll_data->xfds)) {
        revents |= SLIRP_POLL_PRI;
    }
    
    return revents;
}

// Callback functions required by libslirp
static int64_t clock_get_ns(void *opaque) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static ssize_t send_packet(const void *buf, size_t len, void *opaque) {
    dump_buf(buf, len);
    unsigned int protocol = 0;
    unsigned char packet[len];
    unsigned char out[len*2+2];
    size_t outlen = unload_ethernet(buf, len, packet, &protocol);
    if (protocol == 0x0800) {
       fprintf(stderr, "packet response: %d\n", outlen);
       outlen = slip_encode(packet, outlen, out);
       dump_raw(out, outlen);
    }
    return len;
}

static void guest_error(const char *msg, void *opaque) {
    fprintf(stderr, "Guest error: %s\n", msg);
}

static void *timer_new(SlirpTimerCb cb, void *cb_opaque, void *opaque) {
    // Simplified timer implementation
    // In production, you'd need proper timer management
    return malloc(1);
}

static void timer_free(void *timer, void *opaque) {
    free(timer);
}

static void timer_mod(void *timer, int64_t expire_time, void *opaque) {
    // In production, you'd schedule the timer to fire at expire_time
}

static void register_poll_fd(int fd, void *opaque) {
    // Register fd for polling
}

static void unregister_poll_fd(int fd, void *opaque) {
    // Unregister fd from polling
}

static void notify(void *opaque) {
    // Wake up the main loop if it's sleeping
}

Slirp* slirp_init_with_config() {
    // Initialize SLIRP callbacks
    SlirpCb callbacks = {
        .send_packet = send_packet,
        .guest_error = guest_error,
        .clock_get_ns = clock_get_ns,
        .timer_new = timer_new,
        .timer_free = timer_free,
        .timer_mod = timer_mod,
        .register_poll_fd = register_poll_fd,
        .unregister_poll_fd = unregister_poll_fd,
        .notify = notify,
    };

    // Configure SLIRP
    SlirpConfig config = {
        .version = 1,
        .restricted = 0,
        .in_enabled = 1,
        .vnetwork.s_addr = htonl(0x0a000200),        // 10.0.2.0
        .vnetmask.s_addr = htonl(0xffffff00),        // 255.255.255.0
        .vhost.s_addr = htonl(0x0a000202),           // 10.0.2.2
        .vdhcp_start.s_addr = htonl(0x0a00020f),     // 10.0.2.15
        .vnameserver.s_addr = htonl(0x0a000203),     // 10.0.2.3
        .disable_host_loopback = 0,
        .enable_emu = 0,
        .disable_dns = 0,
    };

    // Create SLIRP instance
    Slirp *slirp = slirp_new(&config, &callbacks, NULL);
    if (!slirp) {
        fprintf(stderr, "Failed to create SLIRP instance\n");
        return NULL;
    }

    fprintf(stderr, "SLIRP initialized successfully\n");
    fprintf(stderr, "Virtual network: 10.0.2.0/24\n");
    fprintf(stderr, "Virtual host: 10.0.2.2\n");
    fprintf(stderr, "DHCP start: 10.0.2.15\n");

    return slirp;
}
#endif
