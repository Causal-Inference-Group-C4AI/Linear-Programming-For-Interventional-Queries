\ Model master
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  10000 BaseColumns[0] + 10000 BaseColumns[1] + 10000 BaseColumns[2]
   + 10000 BaseColumns[3] + 10000 BaseColumns[4] + 10000 BaseColumns[5]
   + 10000 BaseColumns[6] + 10000 BaseColumns[7] + 10000 BaseColumns[8]
   + 10000 BaseColumns[9] + 10000 BaseColumns[10] + 10000 BaseColumns[11]
   + 10000 BaseColumns[12] + 10000 BaseColumns[13] + 10000 BaseColumns[14]
   + 10000 BaseColumns[15] + 10000 BaseColumns[16] + 10000 BaseColumns[17]
   + 10000 BaseColumns[18] + 10000 BaseColumns[19] + 10000 BaseColumns[20]
   + 10000 BaseColumns[21] + 10000 BaseColumns[22] + 10000 BaseColumns[23]
   + 10000 BaseColumns[24] + 10000 BaseColumns[25] + 10000 BaseColumns[26]
   + 10000 BaseColumns[27] + 10000 BaseColumns[28] + 10000 BaseColumns[29]
   + 10000 BaseColumns[30] + 10000 BaseColumns[31] + 10000 BaseColumns[32]
   + 10000 BaseColumns[33] + 10000 BaseColumns[34] + 10000 BaseColumns[35]
   + 10000 BaseColumns[36] + 10000 BaseColumns[37] + 10000 BaseColumns[38]
   + 10000 BaseColumns[39] + 10000 BaseColumns[40] + 10000 BaseColumns[41]
   + 10000 BaseColumns[42] + 10000 BaseColumns[43] + 10000 BaseColumns[44]
   + 10000 BaseColumns[45] + 10000 BaseColumns[46] + 10000 BaseColumns[47]
   + 10000 BaseColumns[48] + 10000 BaseColumns[49] + 10000 BaseColumns[50]
   + 10000 BaseColumns[51] + 10000 BaseColumns[52] + 10000 BaseColumns[53]
   + 10000 BaseColumns[54] + 10000 BaseColumns[55] + 10000 BaseColumns[56]
   + 10000 BaseColumns[57] + 10000 BaseColumns[58] + 10000 BaseColumns[59]
   + 10000 BaseColumns[60] + 10000 BaseColumns[61] + 10000 BaseColumns[62]
   + 10000 BaseColumns[63] + 10000 BaseColumns[64]
   + 0.0967199327165685 Variable[65] + 0.0967199327165685 Variable[66]
   + 0.0967199327165685 Variable[67] + 0.0967199327165685 Variable[68]
   + 0.0967199327165685 Variable[69]
Subject To
 EmpiricalRestrictions[0]: BaseColumns[0] + Variable[65] + Variable[66]
   + Variable[67] = 0.4664454148471616
 EmpiricalRestrictions[1]: BaseColumns[1] + Variable[65] + Variable[66]
   + Variable[67] = 0.4728833333333334
 EmpiricalRestrictions[2]: BaseColumns[2] + Variable[65] + Variable[66]
   + Variable[67] = 0.4618525862068966
 EmpiricalRestrictions[3]: BaseColumns[3] + Variable[65] + Variable[66]
   + Variable[67] = 0.4450666666666667
 EmpiricalRestrictions[4]: BaseColumns[4] + Variable[65] + Variable[66]
   + Variable[67] = 0.4514508196721311
 EmpiricalRestrictions[5]: BaseColumns[5] + Variable[65] + Variable[66]
   + Variable[67] = 0.4381125
 EmpiricalRestrictions[6]: BaseColumns[6] + Variable[65] + Variable[66]
   + Variable[67] = 0.5007
 EmpiricalRestrictions[7]: BaseColumns[7] + Variable[65] + Variable[66]
   + Variable[67] = 0
 EmpiricalRestrictions[8]: BaseColumns[8] + Variable[65] + Variable[66]
   + Variable[67] = 0.0080758064516129
 EmpiricalRestrictions[9]: BaseColumns[9] + Variable[65] + Variable[66]
   + Variable[67] = 0
 EmpiricalRestrictions[10]: BaseColumns[10] + Variable[65] + Variable[66]
   + Variable[67] = 0.0455181818181818
 EmpiricalRestrictions[11]: BaseColumns[11] + Variable[65] + Variable[66]
   + Variable[67] = 0
 EmpiricalRestrictions[12]: BaseColumns[12] + Variable[65] + Variable[66]
   + Variable[67] = 0
 EmpiricalRestrictions[13]: BaseColumns[13] + Variable[65] + Variable[66]
   = 0
 EmpiricalRestrictions[14]: BaseColumns[14] + Variable[65] + Variable[67]
   = 0
 EmpiricalRestrictions[15]: BaseColumns[15] + Variable[65] + Variable[66]
   + Variable[67] = 0.0108182225845903
 EmpiricalRestrictions[16]: BaseColumns[16] = 0.0342545851528384
 EmpiricalRestrictions[17]: BaseColumns[17] = 0.0278166666666667
 EmpiricalRestrictions[18]: BaseColumns[18] = 0.0388474137931035
 EmpiricalRestrictions[19]: BaseColumns[19] = 0.0556333333333333
 EmpiricalRestrictions[20]: BaseColumns[20] = 0.0492491803278688
 EmpiricalRestrictions[21]: BaseColumns[21] = 0.0625875
 EmpiricalRestrictions[22]: BaseColumns[22] = 0
 EmpiricalRestrictions[23]: BaseColumns[23] = 0
 EmpiricalRestrictions[24]: BaseColumns[24] = 0.4926241935483872
 EmpiricalRestrictions[25]: BaseColumns[25] = 0.5007
 EmpiricalRestrictions[26]: BaseColumns[26] = 0.4551818181818182
 EmpiricalRestrictions[27]: BaseColumns[27] = 0.5007
 EmpiricalRestrictions[28]: BaseColumns[28] = 0.5007
 EmpiricalRestrictions[29]: BaseColumns[29] + Variable[67] = 0
 EmpiricalRestrictions[30]: BaseColumns[30] + Variable[66] = 0.5007
 EmpiricalRestrictions[31]: BaseColumns[31] = 0.4898817774154097
 EmpiricalRestrictions[32]: BaseColumns[32] + Variable[68] + Variable[69]
   = 0.00780918866080156
 EmpiricalRestrictions[33]: BaseColumns[33] + Variable[68] + Variable[69]
   = 0.014979
 EmpiricalRestrictions[34]: BaseColumns[34] + Variable[68] + Variable[69]
   = 0.00883716814159292
 EmpiricalRestrictions[35]: BaseColumns[35] + Variable[68] + Variable[69]
   = 0
 EmpiricalRestrictions[36]: BaseColumns[36] + Variable[68] + Variable[69]
   = 0.0145427184466019
 EmpiricalRestrictions[37]: BaseColumns[37] + Variable[68] + Variable[69]
   = 0
 EmpiricalRestrictions[38]: BaseColumns[38] + Variable[68] + Variable[69]
   = 0
 EmpiricalRestrictions[39]: BaseColumns[39] + Variable[68] + Variable[69]
   = 0
 EmpiricalRestrictions[40]: BaseColumns[40] + Variable[68] + Variable[69]
   = 0.4826566666666666
 EmpiricalRestrictions[41]: BaseColumns[41] + Variable[68] + Variable[69]
   = 0.4993
 EmpiricalRestrictions[42]: BaseColumns[42] + Variable[68] + Variable[69]
   = 0.4993
 EmpiricalRestrictions[43]: BaseColumns[43] + Variable[68] + Variable[69]
   = 0
 EmpiricalRestrictions[44]: BaseColumns[44] + Variable[68] + Variable[69]
   = 0.4993
 EmpiricalRestrictions[45]: BaseColumns[45] + Variable[68] = 0
 EmpiricalRestrictions[46]: BaseColumns[46] + Variable[68] + Variable[69]
   = 0.4993
 EmpiricalRestrictions[47]: BaseColumns[47] + Variable[68] + Variable[69]
   = 0.4620087202260799
 EmpiricalRestrictions[48]: BaseColumns[48] = 0.4914908113391985
 EmpiricalRestrictions[49]: BaseColumns[49] = 0.484321
 EmpiricalRestrictions[50]: BaseColumns[50] = 0.4904628318584072
 EmpiricalRestrictions[51]: BaseColumns[51] = 0.4993
 EmpiricalRestrictions[52]: BaseColumns[52] = 0.4847572815533981
 EmpiricalRestrictions[53]: BaseColumns[53] = 0.4993
 EmpiricalRestrictions[54]: BaseColumns[54] = 0.4993
 EmpiricalRestrictions[55]: BaseColumns[55] = 0
 EmpiricalRestrictions[56]: BaseColumns[56] = 0.0166433333333333
 EmpiricalRestrictions[57]: BaseColumns[57] = 0
 EmpiricalRestrictions[58]: BaseColumns[58] = 0
 EmpiricalRestrictions[59]: BaseColumns[59] = 0
 EmpiricalRestrictions[60]: BaseColumns[60] = 0
 EmpiricalRestrictions[61]: BaseColumns[61] + Variable[69] = 0
 EmpiricalRestrictions[62]: BaseColumns[62] = 0
 EmpiricalRestrictions[63]: BaseColumns[63] = 0.0372912797739201
 EmpiricalRestrictions[64]: BaseColumns[64] + Variable[65] + Variable[66]
   + Variable[67] + Variable[68] + Variable[69] = 1
Bounds
End
