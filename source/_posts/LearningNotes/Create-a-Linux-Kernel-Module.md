---
title: Create a Linux Kernel Module
date: 2023-10-17 18:15:09
categories: linux-kernel-labs
---

创建一个 `Linux` 内核模块，为 `kernel PWN` 的学习补充一些基础知识。

英文原文链接：

- [Kernel modules — The Linux Kernel documentation (linux-kernel-labs.github.io)](https://linux-kernel-labs.github.io/refs/heads/master/labs/kernel_modules.html)

代码带库：

- [linux-kernel-labs/linux: Linux kernel source tree (github.com)](https://github.com/linux-kernel-labs/linux)

<!-- more -->

# 理论

## 内核模块概述

宏内核虽然比微内核要快，但模块化不足，可扩展性低。在现代宏内核中，通过引入内核模块机制，这个问题被很好地解决了。一个内核模块（或者叫可加载内核层）是一个包含可执行指令的对象文件，在需要时被加载，从而达到在运行时扩展内核功能的目的。当不再需要这个内核模块时，可以把它卸载掉。大部分设备驱动以内核模块的形式被使用。

对于`Linux`设备驱动的开发，一般建议既下载内核源码、配置并编译，同时下载编译好的版本，以便进行测试和开发。

## 内核模块示例

下面是一个非常简单的内核模块示例。当被加载到内核中时，它会生成一个消息 "HI"，当被从卸载时，会生成一个消息 “Bye"。

> 译者注：模块文件名称不能是 module，本文使用 modul

```c
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/module.h>

MODULE_DESCRIPTION("My kernel module");
MODULE_AUTHOR("Me");
MODULE_LICENSE("GPL");

static int dummy_init(void)
{
        printk("Hi\n");
        return 0;
}

static void dummy_exit(void)
{
        printk("Bye\n");
}

module_init(dummy_init);
module_exit(dummy_exit);
```

生成的消息不会在终端中展示，而是会被保存到一个特殊的内存区域，我们可以使用日志守护进程 `syslog` 获取它们。为了展示内核消息，可以使用 `dmesg` 命令或者查看系统日志。

```shell
# dmesg | tail -2
Hi
Bye

# cat /var/log/syslog | tail -2
Feb 20 13:57:38 asgard kernel: Hi
Feb 20 13:57:43 asgard kernel: Bye
```

## 编译内核模块

编译内核模块和编译用户程序有所不同。首先，要使用一些不同的头文件，且模块不应该链接到任何的库。同时，不能不提的是，模块编译选项必须和目标内核编译时用的选项保持一致。出于这些原因，我们可以使用一个标准的内核模块编译方法（kbuild）。这种方法使用到两个文件：一个 `Makefile` 和一个 `Kbuild` 文件。

下面是一个 `Makefile` 的示例：

```makefile
KDIR = /lib/modules/`uname -r`/build
# 译者注：这样得到的内核源码目录不一定正确，还需根据实际情况进行调整

kbuild:
        make -C $(KDIR) M=`pwd`

clean:
        make -C $(KDIR) M=`pwd` clean
```

一个 `Kbuild` 示例：

```shell
EXTRA_CFLAGS = -Wall -g

obj-m        = modul.o
```

正如所见，对 `Makefile` 调用 `make`会导致在内核源码目录（KDIR）中调用 `make`，并引用当前目录（M=`pwd`）。这个过程最终导致从当前目录中读取 `Kbuild` 文件，并按照该文件中的指示编译模块。

>Note.
>
>当使用从其他地方下载来的Linux源码，而不是本机源码时，需调整 KDIR 至对应内核源码目录。
>
>如：KDIR = /home/student/src/linux

`Kbuild` 文件中包含一条或多条用于编译内核模块的指令，最简单的指令示例如：obj-m = module.o  根据这条指令，一个内核模块（内核对象ko - kernel object），会从 `module.o`文件开始创建。`module.o` 会从 `module.c` 或 `module.S` 文件中读取。这些文件都应能在 `Kbuild` 所在目录中找到。

一个使用多个子模块的 `Kbuild` 文件示例如下：

```makefile
EXTRA_CFLAGS = -Wall -g

obj-m = supermodule.o
supermodule-y = module-a.o module-b.o
```

对于上面的示例，编译步骤如下：

- 编译 `module-a.c` 和 `module-b.c` 源码文件，得到 `module-a.c` 和 `module-b.o` 对象文件
- 将 `module-a.c` 和 `module-b.o` 链接成 `supermodule.o`
- 最后从 `supermodule.o` 可以创建 `supermodule.ko` 模块

`Kbuild` 中目标名称的后缀，决定了它们会被如何使用，规则如下：

- M（module）指可加载内核模块目标

- Y（yes）表示一个编译得到的，且还会被链接到内核模块（$(module_name)-y）或链接进内核（obj-y）的对象目标
- 所有其它的目标名称后缀。都会被 `Kbuild`忽略，且对应文件不会被编译。

> Note.
>
> 这些后缀可以方便使用`make menuconfig`命令或直接编辑`.config`文件配置内核。`.config`文件设置了一系列变量，用于确定在构建时将哪些功能添加到内核中。
>
> 例如，当使用`make menuconfig`添加`BTRFS`支持时，会将`CONFIG BTRFS FS=y`行添加到`.config`文件中。原本`BTRFS kbuild`包含行`obj-$（CONFIG BTRFS FS）：=BTRFS.o`，现在该行会变为`obj-y：=BTRFS.`o。这将编译`BTRFS.0`对象并将其链接到内核。在设置变量之前，该行变为`obj:=btrfs.o`，因此它被忽略，构建得到的内核也就不支持`BTRFS `。

## 内核模块的加载和卸载

加载模块使用`insmod`命令，接收内核模块路径作参数；卸载模块使用`rmmod`命令，使用模块名称作为参数。

```shell
$ insmod modul.ko
$ rmmod modul.ko
```

加载内核模块时，会执行被指定为`module_init`宏参数的例程。类似地，当卸载模块时，会执行被指定为`module_exit`宏参数的例程。

一个内核模块完整的编译、加载、卸载的过程如下

```shell
faust:~/lab-01/modul-lin# ls
Kbuild  Makefile  modul.c

faust:~/lab-01/modul-lin# make
make -C /lib/modules/`uname -r`/build M=`pwd`
make[1]: Entering directory `/usr/src/linux-2.6.28.4'
  LD      /root/lab-01/modul-lin/built-in.o
  CC [M]  /root/lab-01/modul-lin/modul.o
  Building modules, stage 2.
  MODPOST 1 modules
  CC      /root/lab-01/modul-lin/modul.mod.o
  LD [M]  /root/lab-01/modul-lin/modul.ko
make[1]: Leaving directory `/usr/src/linux-2.6.28.4'

faust:~/lab-01/modul-lin# ls
built-in.o  Kbuild  Makefile  modul.c  Module.markers
modules.order  Module.symvers  modul.ko  modul.mod.c
modul.mod.o  modul.o

faust:~/lab-01/modul-lin# insmod modul.ko

faust:~/lab-01/modul-lin# dmesg | tail -1
Hi

faust:~/lab-01/modul-lin# rmmod modul

faust:~/lab-01/modul-lin# dmesg | tail -2
Hi
Bye
```

已加载模块的信息，可以通过`lsmod`命令进行查看，也可以通过 `/proc/modules`文件 和 `/sys/module`目录进行查看。

## 内核模块调试

对内核模块进行故障排除比调试常规程序要复杂得多。首先，内核模块中的错误可能导致整个系统阻塞，因此故障排除也就慢很多。为了避免重启，推荐使用虚拟机（如qemu，virtualbox，vmware等）。

当一个包含`bug`的内核模块被加载到内核中时，最终会生成一个内核`oops`。内核`oops`是内核检测到的无效操作，只能由内核产生。对于稳定的内核版本，`oops`的产生几乎可以肯定地意味着内核模块中存在`bug`。在`oops`出现后，内核会继续工作。

保存`oops`出现时内核发出的消息是很重要的，和上面提到的一样，内核产生的消息被保存到日志中，能够使用`dmesg`命令进行展示。为了不丢失任何的内核消息，推荐直接从控制台终端插入/测试内核模块，或者定期查看内核消息。值得注意的是，`oops`的产生既可能是因为一个编程错误，也可能是因为一个错误。

如果出现一个致命的错误，导致系统无法返回到一个稳定态，会产生一个内核`panic`。

下面是一个包含bug，会产生`oops`的内核模块源码示例：

```c
/*
 * Oops generating kernel module
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>

MODULE_DESCRIPTION ("Oops");
MODULE_LICENSE ("GPL");
MODULE_AUTHOR ("PSO");

#define OP_READ         0
#define OP_WRITE        1
#define OP_OOPS         OP_WRITE

static int my_oops_init (void)
{
        int *a;

        a = (int *) 0x00001234;
#if OP_OOPS == OP_WRITE
        *a = 3;
#elif OP_OOPS == OP_READ
        printk (KERN_ALERT "value = %d\n", *a);
#else
#error "Unknown op for oops!"
#endif

        return 0;
}

static void my_oops_exit (void)
{
}

module_init (my_oops_init);
module_exit (my_oops_exit);
```

将这个模块插入到内核中时，会产生一个`oops`：

```c
faust:~/lab-01/modul-oops# insmod oops.ko
[...]

faust:~/lab-01/modul-oops# dmesg | tail -32
BUG: unable to handle kernel paging request at 00001234
IP: [<c89d4005>] my_oops_init+0x5/0x20 [oops]
  *de = 00000000
Oops: 0002 [#1] PREEMPT DEBUG_PAGEALLOC
last sysfs file: /sys/devices/virtual/net/lo/operstate
Modules linked in: oops(+) netconsole ide_cd_mod pcnet32 crc32 cdrom [last unloaded: modul]

Pid: 4157, comm: insmod Not tainted (2.6.28.4 #2) VMware Virtual Platform
EIP: 0060:[<c89d4005>] EFLAGS: 00010246 CPU: 0
EIP is at my_oops_init+0x5/0x20 [oops]
EAX: 00000000 EBX: fffffffc ECX: c89d4300 EDX: 00000001
ESI: c89d4000 EDI: 00000000 EBP: c5799e24 ESP: c5799e24
 DS: 007b ES: 007b FS: 0000 GS: 0033 SS: 0068
Process insmod (pid: 4157, ti=c5799000 task=c665c780 task.ti=c5799000)
Stack:
 c5799f8c c010102d c72b51d8 0000000c c5799e58 c01708e4 00000124 00000000
 c89d4300 c5799e58 c724f448 00000001 c89d4300 c5799e60 c0170981 c5799f8c
 c014b698 00000000 00000000 c5799f78 c5799f20 00000500 c665cb00 c89d4300
Call Trace:
 [<c010102d>] ? _stext+0x2d/0x170
 [<c01708e4>] ? __vunmap+0xa4/0xf0
 [<c0170981>] ? vfree+0x21/0x30
 [<c014b698>] ? load_module+0x19b8/0x1a40
 [<c035e965>] ? __mutex_unlock_slowpath+0xd5/0x140
 [<c0140da6>] ? trace_hardirqs_on_caller+0x106/0x150
 [<c014b7aa>] ? sys_init_module+0x8a/0x1b0
 [<c0140da6>] ? trace_hardirqs_on_caller+0x106/0x150
 [<c0240a08>] ? trace_hardirqs_on_thunk+0xc/0x10
 [<c0103407>] ? sysenter_do_call+0x12/0x43
Code: <c7> 05 34 12 00 00 03 00 00 00 5d c3 eb 0d 90 90 90 90 90 90 90 90
EIP: [<c89d4005>] my_oops_init+0x5/0x20 [oops] SS:ESP 0068:c5799e24
---[ end trace 2981ce73ae801363 ]---
```

尽管相对神秘，内核给出的消息提供了出现`oops`错误的重要信息。第一行：

```shell
BUG: unable to handle kernel paging request at 00001234
EIP: [<c89d4005>] my_oops_init + 0x5 / 0x20 [oops]
```

告诉我们产生错误的原因，和造成错误的指令的地址。本例中，这是一个无效内存地址获取。

下一行

```shell
Oops: 0002 [# 1] PREEMPT DEBUG_PAGEALLOC
```

告诉我们这是第一个`oops`(#1)，在一个`oops`可能导致其它`oops`时，这一点是很重要的。通常，我们要关注的是第一个`oops`。此外，`oops code`（0002）标明了错误类型（见`arch/x86/include/asm/trap_pf.h`）：

- Bit 0 == 0 表示找不到页，1 表示页保护错误
- Bit 1 == 0 表示读，1 表示写
- Bit 2 == 0 表示内核模式，1 表示用户模式

在本例中，产生`oops`(Bit 1 == 1)的原因是，尝试在`内核模式`向一个`找不到的内存页`执行`写操作`。

下面使用`dmesg`产看日志，可以看到寄存器的转储信息，给出了`EIP`寄存器的值，同时可以注意到`bug`出现在`my_oops_init`函数，偏移为5字节(`EIP: [<c89d4005>] my_oops_init+0x5`)（译者注：？），同时消息还展示了堆栈内容和在`oops`出现前的调用回溯。

```plain
faust:~/lab-01/modul-oops# dmesg | tail -33
BUG: unable to handle kernel paging request at 00001234
IP: [<c89c3016>] my_oops_init+0x6/0x20 [oops]
  *de = 00000000
Oops: 0000 [#1] PREEMPT DEBUG_PAGEALLOC
last sysfs file: /sys/devices/virtual/net/lo/operstate
Modules linked in: oops(+) netconsole pcnet32 crc32 ide_cd_mod cdrom

Pid: 2754, comm: insmod Not tainted (2.6.28.4 #2) VMware Virtual Platform
EIP: 0060:[<c89c3016>] EFLAGS: 00010292 CPU: 0
EIP is at my_oops_init+0x6/0x20 [oops]
EAX: 00000000 EBX: fffffffc ECX: c89c3380 EDX: 00000001
ESI: c89c3010 EDI: 00000000 EBP: c57cbe24 ESP: c57cbe1c
 DS: 007b ES: 007b FS: 0000 GS: 0033 SS: 0068
Process insmod (pid: 2754, ti=c57cb000 task=c66ec780 task.ti=c57cb000)
Stack:
 c57cbe34 00000282 c57cbf8c c010102d c57b9280 0000000c c57cbe58 c01708e4
 00000124 00000000 c89c3380 c57cbe58 c5db1d38 00000001 c89c3380 c57cbe60
 c0170981 c57cbf8c c014b698 00000000 00000000 c57cbf78 c57cbf20 00000580
Call Trace:
 [<c010102d>] ? _stext+0x2d/0x170
 [<c01708e4>] ? __vunmap+0xa4/0xf0
 [<c0170981>] ? vfree+0x21/0x30
 [<c014b698>] ? load_module+0x19b8/0x1a40
 [<c035d083>] ? printk+0x0/0x1a
 [<c035e965>] ? __mutex_unlock_slowpath+0xd5/0x140
 [<c0140da6>] ? trace_hardirqs_on_caller+0x106/0x150
 [<c014b7aa>] ? sys_init_module+0x8a/0x1b0
 [<c0140da6>] ? trace_hardirqs_on_caller+0x106/0x150
 [<c0240a08>] ? trace_hardirqs_on_thunk+0xc/0x10
 [<c0103407>] ? sysenter_do_call+0x12/0x43
Code: <a1> 34 12 00 00 c7 04 24 54 30 9c c8 89 44 24 04 e8 58 a0 99 f7 31
EIP: [<c89c3016>] my_oops_init+0x6/0x20 [oops] SS:ESP 0068:c57cbe1c
---[ end trace 45eeb3d6ea8ff1ed ]---
```

如果生成一个无效的读调用(`#define OP_OOPS OP_READ`)，消息基本会是相同的，但是`oops code`会变成 `0000`。

### objdump

使用`objdump`工具，可以获得导致`oops`的指令的详细信息。常用指令有两个，`-d`用于反汇编，`-S`用于交织显示`C`代码和汇编代码，一般组合使用`-dS`。为了提高解码效率，我们需要用到内核模块的加载地址，它可以在`/proc/modules`中找到。

下面是一个示例，对上面的内核模块使用`objdump`命令，识别生成`oops`的指令：

```shell
faust:~/lab-01/modul-oops# cat /proc/modules
oops 1280 1 - Loading 0xc89d4000
netconsole 8352 0 - Live 0xc89ad000
pcnet32 33412 0 - Live 0xc895a000
ide_cd_mod 34952 0 - Live 0xc8903000
crc32 4224 1 pcnet32, Live 0xc888a000
cdrom 34848 1 ide_cd_mod, Live 0xc886d000

faust:~/lab-01/modul-oops# objdump -dS --adjust-vma=0xc89d4000 oops.ko

oops.ko:     file format elf32-i386


Disassembly of section .text:

c89d4000 <init_module>:
#define OP_READ         0
#define OP_WRITE        1
#define OP_OOPS         OP_WRITE

static int my_oops_init (void)
{
c89d4000:       55                      push   %ebp
#else
#error "Unknown op for oops!"
#endif

        return 0;
}
c89d4001:       31 c0                   xor    %eax,%eax
#define OP_READ         0
#define OP_WRITE        1
#define OP_OOPS         OP_WRITE

static int my_oops_init (void)
{
c89d4003:       89 e5                   mov    %esp,%ebp
        int *a;

        a = (int *) 0x00001234;
#if OP_OOPS == OP_WRITE
        *a = 3;
c89d4005:       c7 05 34 12 00 00 03    movl   $0x3,0x1234
c89d400c:       00 00 00
#else
#error "Unknown op for oops!"
#endif

        return 0;
}
c89d400f:       5d                      pop    %ebp
c89d4010:       c3                      ret
c89d4011:       eb 0d                   jmp    c89c3020 <cleanup_module>
c89d4013:       90                      nop
c89d4014:       90                      nop
c89d4015:       90                      nop
c89d4016:       90                      nop
c89d4017:       90                      nop
c89d4018:       90                      nop
c89d4019:       90                      nop
c89d401a:       90                      nop
c89d401b:       90                      nop
c89d401c:       90                      nop
c89d401d:       90                      nop
c89d401e:       90                      nop
c89d401f:       90                      nop

c89d4020 <cleanup_module>:

static void my_oops_exit (void)
{
c89d4020:       55                      push   %ebp
c89d4021:       89 e5                   mov    %esp,%ebp
}
c89d4023:       5d                      pop    %ebp
c89d4024:       c3                      ret
c89d4025:       90                      nop
c89d4026:       90                      nop
c89d4027:       90                      nop
```

可以看到，上面得到的造成`oops`的指令的地址（c89d4005）处的内容是：

```shell
C89d4005: c7 05 34 12 00 00 03 movl $ 0x3,0x1234
```

这正是我们期望的——在`0x0001234`处存储`3`。

`/proc/modules`中包含内核模块的加载地址，`--adjust-vma`选项允许我们展示和`0xc89d4000`相关的指令。

`-l`选项展示插入到汇编代码中的`C`源码的行号。

### addr2line

一个更简单地找到造成`oops`的指令的方式，是使用`addr2line`工具：

```
faust:~/lab-01/modul-oops# addr2line -e oops.o 0x5
/root/lab-01/modul-oops/oops.c:23
```

其中`0x5`是生成`oops`的指令的程序计数（`EIP=c89d4005`）减去模块加载基址（0xc89d4000，可在`/proc/modules`中查看）后的值。

### minicom

`minicom`（或其他等效程序，如 `picocom`, `screen`），是一个能够用于连接串行端口并与之交互的工具。使用串行端口实在开发阶段分析内核消息或与嵌入式系统进行交互的基本方法。有两种常见的连接方式：

- 我们将使用的设备的**串行端口**是`/dev/ttyS0`
- 我们将使用的设备的`USB`端口（FTDI）是`/dev/ttyUSB`

如果使用虚拟机，虚拟机启动时会显示我们使用的设备。

```shell
char device redirected to /dev/pts/20 (label virtiocon0)
```

`minicom`使用示例：

```shell
# 使用COM1连接，115,200比特率
minicom -b 115200 -D /dev/ttyS0

# USB串行端口连接
minicom -D /dev/ttyUSB0

# 连接虚拟机的串行端口
minicom -D /dev/pts/20
```

### netconsole

`netconsole`是一个可以使用**网络**打印内核日志消息的工具，当磁盘日志系统无法工作、串行端口无法使用或终端没有回显时，使用`netconsole`很合适。`netconsole`本身以内核模块的形式存在。

工作时需要以下参数：

- 端口@IP 地址/调试站的源接口名称
- 端口@调试消息被发送到的机器的 IP 地址/MAC 地址

这些参数可以在模块被**插入内核时**进行配置，也可以在**模块插入后**进行配置（要求编译时开启了 `CONFIG_NETCONSOLE_DYNAMIC` 选项）。

将`netconsole`插入内核时的一个配置示例如下：

```shell
alice:~# modprobe netconsole netconsole=6666@192.168.191.130/eth0,6000@192.168.191.1/00:50:56:c0:00:08
```

IP 地址为`192.168.191.130`的源机器上的调试信息，会经过`6666`端口上的`eth0`接口，发送到 IP 地址为`192.168.191.1` MAC 地址为`00:50:56:c0:00:08`的目标机器的`6000`端口。

在目标机器上可以使用`netcat`接收消息：

```shell
bob:~ # nc -l -p 6000 -u
```

或者，目标机器上可以配置`syslogd`来拦截这些消息。更多信息可在`Documentation/networking/netconsole.txt`中找到。

### Printk 调试

> 两个最经典、最有用的调试工具是你的大脑和 Printf。

对于调试，大家经常使用一种原始但非常高效的方式：`printk`调试。尽管可以使用调试器，但它通常不是很有用：简单的`bug`（比如未初始化的变量，内存管理问题等）可以通过控制消息打印或观察解码后的内核`oops`信息快速定位。

对于更复杂的`bug`，即便是调试器也没办法给予我们太多帮助，除非操作系统的结构非常好理解。当调试内核模块时，存在很多位置的因素：多个上下文（同一时刻系统里运行着多个进程和线程），中断，虚拟内存等等。

你可以使用`printk`把内核消息展示到用户空间。它和`printf`的功能相似，唯一的区别是，传输的消息可以以字符串”`<n>`"为前缀，其中`n`表示错误级别（日志级别），值的范围是`0-7`。如果不使用”`<n>`"，也可以使用一些符号常量表示日志级别，对应关系如下：

```shell
n = 0	KERN_EMERG
n = 1	KERN_ALERT
n = 2	KERN_CRIT
n = 3	KERN_ERR
n = 4	KERN_WARNING
n = 5	KERN_NOTICE
n = 6	KERN_INFO
n = 7	KERN_DEBUG
```

关于所有日志级别的定义，可以在`linux/kern_levels.h`文件中找到。基本上，这些级别主要用于告诉系统要把消息发送到哪里：终端，日志文件，或者 `/var/log` 等等。

>Note.
>
>为了在用户空间展示`printk`消息，消息的日志级别必须比`console_loglevel `的级别要高（数值要小）。默认的终端日志级别可以在`/proc/sys/kernel/printk`进行配置。
>
>比如，
>
>```shell
>echo 8 > /proc/sys/kernel/printk
>```
>
>以上命令将使得所有内核日志消息都能够在终端中展示。也就是说，日志记录级别必须严格小于`console_loglevel`变量。例如，如果`console_loglevel`的值为 5（`KERN_NOTICE`），则只显示`loglevel<=5`的消息（即KERN_EMERG、KERN_ALERT、KERN_CRIT、KERN_ERR、KERN_WARNING）。

控制台重定向消息对于快速查看执行内核代码的效果非常有用，但如果内核遇到无法修复的错误并且系统冻结，它们就不再那么有用了。

在这种情况下，必须查阅系统的日志，因为它们在系统重新启动之间保留信息。这些文件位于`/var/log`中，是文本文件，在内核运行期间由`syslogd`和`klogd`填充。`syslogd`和`klogd`从装载的`/proc`虚拟文件系统中获取信息。原则上，打开`syslogd`和`klogd`后，所有来自内核的消息都将转到`/var/log/kern.log`。

一个更简单的调试方法是使用`/var/log/debug`文件。它只由来自内核的具有`KERN_DEBUG`日志级别的printk消息填充。

考虑到生产内核（类似于我们可能正在运行的内核）只包含**发布代码**，我们的模块是少数几个发送以`KERN DEBUG`为前缀的消息的模块之一。通过这种方式，我们可以通过查找与模块的调试会话相对应的消息，轻松地浏览`/var/log/debug`信息。

示例如下：

```shell
# Clear the debug file of previous information (or possibly a backup)
$ echo "New debug session" > /var/log/debug
# Run the tests
# If there is no critical error causing a panic kernel, check the output
# if a critical error occurs and the machine only responds to a restart,
  restart the system and check /var/log/debug.
```

为了检测错误，打印出的消息应当尽量包含所有感兴趣的信息，但在代码中插入`printk`可能与编写解决问题的代码一样耗时。因此通常需要是调试消息完整性和将这些消息插入代码所需时间之间进行权衡。

可以使用预定义的常量`__FILE__`, `__LINE__` and `__func__`来提高插入`printk`语句的效率：

- `__FILE__`被编译器替换为**源文件**的名称

- `__LINE__`被编译器替换为当前指令对应的源文件中代码的**行号**
- `__func__/__FUNCTION__`被编译器替换为当前指令**所在函数**的名称

>Note.
>
>`__FILE__`和`__LINE__`是`ANSI C`规范的一部分：`__func_`是`C99`规范的一部分；`__FUNCTION __`是一个`GNU C`扩展，不可移植；不过，由于我们为`Linux`内核编写代码，因此可以毫无问题地使用它们。

下面的**宏定义**可以在这样的情况下使用：

```shell
#define PRINT_DEBUG \
       printk (KERN_DEBUG "[% s]: FUNC:% s: LINE:% d \ n", __FILE__,
               __FUNCTION__, __LINE__)
```

之后，在每个我们想要观察是否执行到的位置，插入`PRINT_DEBUG`即可。这是一个简单快速的方式，且可以用于仔细的分系。

`dmesg`命令被用来观察使用`printk`打印，但未在终端输出的消息。

运行以下命令，可以删除日志文件中之前的消息：

```shell
cat /dev/null > /var/log/debug
```

运行以下命令，可以删除当前能被`dmesg`输出的消息：

```shell
dmesg -c
```

### dyndbg 动态调试

动态调试能够显著地减少要输出的消息的数量。为了使用动态调试函数，编译内核时要开启`CONFIG_DYNAMIC_DEBUG`选项，之后就可以使用`pr_debug()`, `dev_dbg()`, `print_hex_dump_debug()`, `print_hex_dump_bytes()`等函数。

当`debugfs`被挂载到`/sys/kernel/debug`时，`/sys/kernel/debug/dynamic_debug/control`文件用于过滤消息，也可以通过它查看已经存在的过滤器。

```shell
mount -t debugfs none /debug
```

`Debugfs`是一个简单的文件系统，用作内核空间接口和用户空间接口来配置不同的调试选项。任何调试工具都可以在`debugfs`中创建和使用自己的文件/文件夹。

比如，为了展示动态调试（dyndbg）中已经存在的过滤器，可以使用：

```shell
cat /debug/dynamic_debug/control
```

如郭想要接收`svsock.c`文件的第**1603**行输出的调试消息，可以使用以下命令进行设置：

```shell
echo 'file svcsock.c line 1603 +p' > /debug/dynamic_debug/control
```

#### 动态调试选项

- func - 根据所在函数的函数名过滤消息

  ```shell
  echo 'func svc_tcp_accept +p' > /debug/dynamic_debug/control
  ```

- file - 根据源文件名过滤消息，可以使用绝对路径和相对路径，以及内核树路径

  ```shell
  file svcsock.c
  file kernel/freezer.c
  file /usr/src/packages/BUILD/sgi-enhancednfs-1.4/default/net/sunrpc/svcsock.c
  ```

- module - 根据模块名过滤消息

  ```shell
  module sunrpc
  ```

- format - 只显示包含以下字符串的消息

  ```shell
  format "nfsd: SETATTR"
  ```

- line - 根据行号启用调试函数

  ```shell
  # Triggers debug messages between lines 1603 and 1605 in the svcsock.c file
  $ echo 'file svcsock.c line 1603-1605 +p' > /sys/kernel/debug/dynamic_debug/control
  # Enables debug messages from the beginning of the file to line 1605
  $ echo 'file svcsock.c line -1605 +p' > /sys/kernel/debug/dynamic_debug/control
  ```

除了以上选项，还可以使用操作符（`+` ` -` ` =`）添加、删除或设置一系列`flags`

- p  激活`pr_debug()`
- f 在输出消息中包含函数名
- l 在输出消息中包含行号
- m 在输出消息中包含模块名
- t 在输出消息中包含线程 id ，如果不是从中断上下文中调用的话
- _ 不设置任何标志

### KDB内核调试器

内核调试器已被证明对促进开发和调试过程非常有用。它的主要优点之一是可以执行实时调试。这使我们能够实时监控对内存的访问，甚至在调试时修改内存。从`2.6.26-rci`版本开始，调试器已经集成在主流内核中。KDB不是源调试器，但要进行完整的分析，它可以并行使用`gdb`和符号文件——请参阅[gdb调试部分](https://linux-kernel-labs.github.io/refs/heads/master/so2/lab1-intro.html#gdb-intro)

要使用`KDB`，有以下选项：

- 非`usb`键盘+`VGA`文本控制台

- 串行端口控制台

- `USB EHCI`调试端口

对于本实验，我们将使用连接到主机的串行接口。以下命令将通过串行端口激活GDB：

```shell
echo hvc0 > /sys/module/kgdboc/parameters/kgdboc
```

`KDB`是一个`stop`模式调试器，这意味着当它处于活动状态时，所有其他进程都会停止。在执行过程中，可以使用以下`Sys Rq`命令强制内核进入`KDB`

```shell
echo g > /proc/sysrq-trigger
```

或者通过在连接到串行端口（例如使用minicom）的终端中使用组合键`Ctrl+O g`。

KDB有各种命令来控制和定义被调试系统的上下文：

- lsmod、ps、kill、dmesg、env、bt（backtrace，回溯）

- 转储跟踪日志

- 硬件断点

- 修改内存

为了更好地描述可用的命令，可以使用`KDBshell`中的`help`命令。在下一个示例中，您可以注意到一个简单的`KDB`使用示例，它设置了一个硬件断点来监视`mVar`变量的更改

```shell
# trigger KDB
echo g > /proc/sysrq-trigger
# or if we are connected to the serial port issue
Ctrl-O g
# breakpoint on write access to the mVar variable
kdb> bph mVar dataw
# return from KDB
kdb> go
```

> Note.
>
> 如果你想学习如何轻松浏览Linux源代码以及如何调试内核代码，请阅读“[Good to know](https://linux-kernel-labs.github.io/refs/heads/master/so2/lab1-intro.html#good-to-know) ”部分。

# 练习

### 基本准备

下载内核源码

```shell
cd ~
curl -O -L https://mirrors.tuna.tsinghua.edu.cn/kernel/v5.x/linux-5.4.98.tar.xz
unxz linux-5.4.98.tar.xz
tar -xf linux-5.4.98.tar
```

配置编译选项，

```shell
make menuconfig
# 依次进入到 Kernel hacking -> Compile-time checks and compiler options，然后勾选如下选项Compile the kernel with debug info，以便于调试
# 如果要使用 kgdb 调试内核，则需要选中 KGDB: kernel debugger，并选中 KGDB 下的所有选项。
```

根据配置准备必要文件

```shell
make prepare
```

创建内核模块实验目录

```
mkdir linuxkm
code linuxkm  # 使用vscode
```

设置vscode 头文件目录，添加以下三个路径，如果头文件仍然显示错误，建议禁用错误波形曲线

```
~/linux-5.4.98/include/**
~/linux-5.4.98/arch/x86/include/**
"~/linux-5.4.98/arch/x86/include/generated/**"
```

Makefile

```makefile
KDIR =  ~/linux-5.4.98/

kbuild:
	make -C $(KDIR) M=`pwd`

clean:
	make -C $(KDIR) M=`pwd` clean

.PHONY: kbuild clean
```

Kbuild

```makefile
EXTRA_CFLAGS = -Wall -g

obj-m        = modul.o
```

modul.c

```c
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/module.h>

MODULE_DESCRIPTION("My kernel module");
MODULE_AUTHOR("Me");
MODULE_LICENSE("GPL");

static int dummy_init(void)
{
        printk("Hi\n");
        return 0;
}

static void dummy_exit(void)
{
        printk("Bye\n");
}

module_init(dummy_init);
module_exit(dummy_exit);
```

执行make命令，输出以下内容则编译成功

```shell
~/linuxkm$ make
make -C ~/linux-5.4.98/ M=`pwd`
make[1]: Entering directory '/home/czx/linux-5.4.98'
  CC [M]  /mnt/d/Users/czx/NativeFiles/Desktop/PWN/linuxkm/modul.o

  WARNING: Symbol version dump ./Module.symvers
           is missing; modules will have no dependencies and modversions.

  Building modules, stage 2.
  MODPOST 1 modules
  CC [M]  /mnt/d/Users/czx/NativeFiles/Desktop/PWN/linuxkm/modul.mod.o
  LD [M]  /mnt/d/Users/czx/NativeFiles/Desktop/PWN/linuxkm/modul.ko
make[1]: Leaving directory '/home/czx/linux-5.4.98'
```

### 启动虚拟机

```

```

执行 make boot

```shell
tools/labs$ make boot
qemu/create_net.sh lkt-tap0
qemu/create_net.sh lkt-tap1
/home/czx/linux-kernel-labs/tools/labs/templates/assignments/6-e100/nttcp -v -i &
nttcp-l: nttcp, version 1.47
nttcp-l: running in inetd mode on port 5037 - ignoring options beside -v and -p
bind: Address already in use
nttcp-l: service-socket: bind:: Address already in use, errno=98
ARCH=x86 qemu/qemu.sh -kernel /home/czx/linux-kernel-labs/arch/x86/boot/bzImage -device virtio-serial -chardev pty,id=virtiocon0 -device virtconsole,chardev=virtiocon0 -serial pipe:pipe1 -serial pipe:pipe2 -netdev tap,id=lkt-tap0,ifname=lkt-tap0,script=no,downscript=no -net nic,netdev=lkt-tap0,model=virtio -netdev tap,id=lkt-tap1,ifname=lkt-tap1,script=no,downscript=no -net nic,netdev=lkt-tap1,model=i82559er -drive file=core-image-minimal-qemux86.ext4,if=virtio,format=raw -drive file=disk1.img,if=virtio,format=raw -drive file=disk2.img,if=virtio,format=raw --append "root=/dev/vda loglevel=15 console=hvc0 pci=noacpi" --display none -s -m 256
char device redirected to /dev/pts/9 (label virtiocon0)
```

使用 minicom 登录qemu，注意 -D 后的设备号与上面输出的最后一行保持一致，进入时输入root，即获得shell界面

```shell
minicom -D /dev/pts/9
或
minicom -D serial.pts
```

### 内核模块



### Printk



### Error



### Sub-modules



### Kernel oops



### Module parameters



### proc info