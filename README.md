# NB-SSH

Source code for the following paper.

`
Xiaojun Zhu, Jiao Tang. "NB-SSH: NB-IoT-Based Remote SSH Access to UAVs under Symmetric NAT." IEEE Networking Letters, 6(1), pages 6-10, March 2024.`https://doi.org/10.1109/LNET.2023.3323389

If you find the software helpful, please cite the paper.

## Introduction
NB-SSH enables clients to ssh into remote UAVs equipped with NB-IoT, even if the NB-IoT is behind symmetric NAT and has no global IP address.

There are two variants: a socket-forwarding variant and a TUN-based variant, corresponding to two folders.

![NB-SSH](https://gitee.com/idletom/typora-picgo/raw/master/img/NB-SSH.png)



## Socket-Forwarding

The folder contains two Python files, one for UAV and one for the cloud server. The Management Host does not install any software.

Run the program at the cloud server, and then run the program for the UAV. The management host is then able to ssh into the UAV.


## TUN

The folder contains three Python files for the three entities. Both the UAV and the Management Host need to build a local TUN interface.

The TUN interface is built based on the **[pytun](https://github.com/montag451/pytun)**.

Environment: Linux, NB-IoT, Python\>=3.6

1. Install `pytun`

```bash
pip install python-pytun==2.4.1
```

2. Run the program in order

```bash
Cloud Server, UAV, Management Host
```

Then run the ssh command in the management host. Note that the destination should be the UAV's IP address of the TUN interface.




