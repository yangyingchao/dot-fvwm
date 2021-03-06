gap_y 80
alignment top_left

# set to yes if you want all text to be in uppercase
uppercase no
#avoid flicker
double_buffer yes
no_buffers yes

#own window to run simultanious 2 or more conkys
own_window yes
own_window_type normal
own_window_hints undecorate,sticky,skip_taskbar,skip_pager
own_window_transparent yes


#shades
draw_shades no
#draw_graph_borders yes
#draw_borders yes

#borders
draw_borders no

# Force UTF8? note that UTF8 support required XFT
override_utf8_locale yes

#to prevent window from moving
use_spacer no


TEXT
${color #a40000}System Info ${color}
${color #c4a000}Kernel: $alignr${color dcff82}$kernel${color}${color}
${color #c4a000}Time: $alignr${color dcff82}${time %D %H:%M}${color}${color}
${color #c4a000}UpTime: $alignr${color dcff82}${uptime %H:%M}${color}${color}
${color #c4a000}CPU I ${color dcff82}${cpu cpu1}%${color} ${color #c4a000}CPU II${color} ${color dcff82}${cpu cpu2}%${color}${color}
${color #c4a000}Mem: ${color dcff82}${font}${mem} ($memperc%)${color}
${color #dcff82}${membar 4,200}
${color #c4a000}Processes: ${color dcff82}${font}${processes} ${color}
${color #c4a000}Running: ${color dcff82}${font}${running_processes} ${color}
${color slate grey}TOP 3:$alignr        -PID-  CPU%   $color
${color #ef2929}${top name 1}$alignr${top pid 1}${top cpu 1}
${color lightgrey}${top name 2}$alignr${top pid 2}${top cpu 2}
${color lightgrey}${top name 3}$alignr${top pid 3}${top cpu 3}

${color #a40000}Network Info ETH0${color}
${color #c4a000}IP Addr: ${color #dcff82}${addr enp2s0f0}${color}
${color #c4a000}Down: ${color #dcff82}${downspeed enp2s0f0}${color}${color} #${color #dcff82}  ${totaldown enp2s0f0}${color}${color}

${color #c4a000}Up:   ${color #dcff82}${upspeed enp2s0f0}${color}${color #dcff82} #${totalup enp2s0f0}

${color #a40000}File System ${color}
${color #c4a000}Disk IO: ${color #dcff82}${alignr 4}$diskio ${color} ${color}
${color #c4a000}Root: ${color}${alignr}${color #dcff82}${fs_free /}${color} Free ${color}
${color #dcff82}${fs_bar 4 /}
${color #c4a000}HOME: ${color}${alignr}${color #dcff82}${fs_free /home}${color} Free ${color}
${color #dcff82}${fs_bar 4 /home}${color}
