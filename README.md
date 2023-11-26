In the field of protocol engineering, I've faced some challenges, espcially when dealing with log areas lacking parsing. In such cases, I try to interpret them based on 3GPP standards. This led me to study relevant standards and develop a Python tool capable of taking hex values as input and providing the desired decoding results. 

I'm focused on creating a tool capable of analyzing URSP rules found in the UE Policy Container for network slicing, a core technology in 5G. URSP rules contain 5GSM PDU session routing information for a specific service or application when activated, and they can be set on the device through Pre-configured or NW provisioning methods. In the Pre-configured method, URSP rules can be stored on the device's NV or SIM EF_URSP. In the NW provisioning method, URSP rules are created on the 5GC PCF and remotely updated on the device.

However, the early development stage of PCF presents challenges, such as limited functionality—allowing only one URSP rule configuration and constraints on Traffic Descriptor type options. To address this, I created a tool for decoding/encoding URSP rules from/to hex values. Notably, the resulting encoded hex values containing URSP rules can be stored in SIM through AT command, enabling tesing of various network slicing scenarios without relying on PCF.

In conclusion, the tool I devloped comprises two main functionalities: encoding and decoding URSP rules. The encoding functionality allows users to create desired URSP rules based on the designed GUI, while the decoding functionality interprets hex values received from PCF through a simple copy-paste operation, providing an interpreted output.

Here is a sample of program execution.

1. URSP rule encoding
![image](https://github.com/joostone-ahn/URSP_Analyzer/assets/98713651/dcd783df-dfe5-4303-b45f-62feab5b7b85)
![image](https://github.com/joostone-ahn/URSP_Analyzer/assets/98713651/ba3b1162-8404-4d0a-9bac-5060dea8ba76)


2. URSP rule decoding
![image](https://github.com/joostone-ahn/URSP_Analyzer/assets/98713651/94341c95-5545-4749-858d-dd41411878a2)
![image](https://github.com/joostone-ahn/URSP_Analyzer/assets/98713651/fa0a8ea3-11c2-45c1-862e-de2a83d8186f)
