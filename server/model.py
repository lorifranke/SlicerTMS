import torch.nn as nn
import torch
import torch.nn.functional as F
import pdb

class Modified3DUNet(nn.Module):
	def __init__(self, in_channels, n_classes, base_n_filter = 8):
		super(Modified3DUNet, self).__init__()
		self.in_channels = in_channels
		self.n_classes = n_classes
		self.base_n_filter = base_n_filter

		self.lrelu = nn.LeakyReLU()
		self.dropout3d = nn.Dropout3d(p=0.6)
		self.upsacle = nn.Upsample(scale_factor=2, mode='nearest')
#		self.softmax = nn.Softmax(dim=1)

		# Level 1 context pathway
		self.conv3d_c1_1 = nn.Conv3d(self.in_channels, self.base_n_filter, kernel_size=3, stride=1, padding=1, bias=False)
		self.conv3d_c1_2 = nn.Conv3d(self.base_n_filter, self.base_n_filter, kernel_size=3, stride=1, padding=1, bias=False)
		self.lrelu_conv_c1 = self.lrelu_conv(self.base_n_filter, self.base_n_filter)
		self.inorm3d_c1 = nn.InstanceNorm3d(self.base_n_filter)

		# Level 2 context pathway
		self.conv3d_c2 = nn.Conv3d(self.base_n_filter, self.base_n_filter*2, kernel_size=3, stride=2, padding=1, bias=False)
		self.norm_lrelu_conv_c2 = self.norm_lrelu_conv(self.base_n_filter*2, self.base_n_filter*2)
		self.inorm3d_c2 = nn.InstanceNorm3d(self.base_n_filter*2)

		# Level 3 context pathway
		self.conv3d_c3 = nn.Conv3d(self.base_n_filter*2, self.base_n_filter*4, kernel_size=3, stride=2, padding=1, bias=False)
		self.norm_lrelu_conv_c3 = self.norm_lrelu_conv(self.base_n_filter*4, self.base_n_filter*4)
		self.inorm3d_c3 = nn.InstanceNorm3d(self.base_n_filter*4)

		# Level 4 context pathway
		self.conv3d_c4 = nn.Conv3d(self.base_n_filter*4, self.base_n_filter*8, kernel_size=3, stride=2, padding=(1,1,1), bias=False)
		self.norm_lrelu_conv_c4 = self.norm_lrelu_conv(self.base_n_filter*8, self.base_n_filter*8)
		self.inorm3d_c4 = nn.InstanceNorm3d(self.base_n_filter*8)

		# Level 5 context pathway, level 0 localization pathway
		self.conv3d_c5 = nn.Conv3d(self.base_n_filter*8, self.base_n_filter*16, kernel_size=3, stride=2, padding=1, bias=False)
		self.norm_lrelu_conv_c5 = self.norm_lrelu_conv(self.base_n_filter*16, self.base_n_filter*16)
		self.norm_lrelu_upscale_conv_norm_lrelu_l0 = self.norm_lrelu_upscale_conv_norm_lrelu(self.base_n_filter*16, self.base_n_filter*8)

		self.conv3d_l0 = nn.Conv3d(self.base_n_filter*8, self.base_n_filter*8, kernel_size = 1, stride=1, padding=(0,0,0), bias=False)
		self.inorm3d_l0 = nn.InstanceNorm3d(self.base_n_filter*8)

		# Level 1 localization pathway
		self.conv_norm_lrelu_l1 = self.conv_norm_lrelu(self.base_n_filter*16, self.base_n_filter*16)
		self.conv3d_l1 = nn.Conv3d(self.base_n_filter*16, self.base_n_filter*8, kernel_size=1, stride=1, padding=0, bias=False)
		self.norm_lrelu_upscale_conv_norm_lrelu_l1 = self.norm_lrelu_upscale_conv_norm_lrelu(self.base_n_filter*8, self.base_n_filter*4)

		# Level 2 localization pathway
		self.conv_norm_lrelu_l2 = self.conv_norm_lrelu(self.base_n_filter*8, self.base_n_filter*8)
		self.conv3d_l2 = nn.Conv3d(self.base_n_filter*8, self.base_n_filter*4, kernel_size=1, stride=1, padding=0, bias=False)
		self.norm_lrelu_upscale_conv_norm_lrelu_l2 = self.norm_lrelu_upscale_conv_norm_lrelu(self.base_n_filter*4, self.base_n_filter*2)

		# Level 3 localization pathway
		self.conv_norm_lrelu_l3 = self.conv_norm_lrelu(self.base_n_filter*4, self.base_n_filter*4)
		self.conv3d_l3 = nn.Conv3d(self.base_n_filter*4, self.base_n_filter*2, kernel_size=1, stride=1, padding=0, bias=False)
		self.norm_lrelu_upscale_conv_norm_lrelu_l3 = self.norm_lrelu_upscale_conv_norm_lrelu(self.base_n_filter*2, self.base_n_filter)

		# Level 4 localization pathway
		self.conv_norm_lrelu_l4 = self.conv_norm_lrelu(self.base_n_filter*2, self.base_n_filter*2)
		self.conv3d_l4 = nn.Conv3d(self.base_n_filter*2, self.n_classes, kernel_size=1, stride=1, padding=0, bias=False)

		self.ds2_1x1_conv3d = nn.Conv3d(self.base_n_filter*8, self.n_classes, kernel_size=1, stride=1, padding=0, bias=False)
		self.ds3_1x1_conv3d = nn.Conv3d(self.base_n_filter*4, self.n_classes, kernel_size=1, stride=1, padding=0, bias=False)
        # ap: regression
		self.rg4_1x1_conv3d = nn.Conv3d(self.n_classes, self.n_classes, kernel_size=1, stride=1, padding=0, bias=False)


	def conv_norm_lrelu(self, feat_in, feat_out):
		return nn.Sequential(
			nn.Conv3d(feat_in, feat_out, kernel_size=3, stride=1, padding=1, bias=False),
			nn.InstanceNorm3d(feat_out),
			nn.LeakyReLU())

	def norm_lrelu_conv(self, feat_in, feat_out):
		return nn.Sequential(
			nn.InstanceNorm3d(feat_in),
			nn.LeakyReLU(),
			nn.Conv3d(feat_in, feat_out, kernel_size=3, stride=1, padding=1, bias=False))

	def lrelu_conv(self, feat_in, feat_out):
		return nn.Sequential(
			nn.LeakyReLU(),
			nn.Conv3d(feat_in, feat_out, kernel_size=3, stride=1, padding=1, bias=False))

	def norm_lrelu_upscale_conv_norm_lrelu(self, feat_in, feat_out):
		return nn.Sequential(
			nn.InstanceNorm3d(feat_in),
			nn.LeakyReLU(),
			nn.Upsample(scale_factor=2, mode='nearest'),
			# should be feat_in*2 or feat_in
			nn.Conv3d(feat_in, feat_out, kernel_size=3, stride=1, padding=1, bias=False),
			nn.InstanceNorm3d(feat_out),
			nn.LeakyReLU())
        
	def forward(self, x):
		#  Level 1 context pathway
		out = self.conv3d_c1_1(x) # y: 1-16-70-90-50
		# print("level_1 out size", out.size())
		residual_1 = out
		out = self.lrelu(out) 
		out = self.conv3d_c1_2(out)
		out = self.dropout3d(out)
		out = self.lrelu_conv_c1(out)
		# Element Wise Summation
		out += residual_1
		context_1 = self.lrelu(out)# context_1: 1-16-70-90-50
		# print("context_1 size", out.size())
		out = self.inorm3d_c1(out)
		out = self.lrelu(out)

		# Level 2 context pathway
		out = self.conv3d_c2(out) # y: 1-32-35-45-25
		#print("level_2 out size", out.size())
		residual_2 = out
		out = self.norm_lrelu_conv_c2(out)
		out = self.dropout3d(out)
		out = self.norm_lrelu_conv_c2(out)
		out += residual_2
		out = self.inorm3d_c2(out)
		out = self.lrelu(out)
		context_2 = out # context_2: 1-32-35-45-25
		#print("context_2 size", out.size())

		# Level 3 context pathway
		out = self.conv3d_c3(out) # y: 1-64-18-23-13
		#print("level_3 out size", out.size())
		residual_3 = out
		out = self.norm_lrelu_conv_c3(out)
		out = self.dropout3d(out)
		out = self.norm_lrelu_conv_c3(out)
		out += residual_3
		out = self.inorm3d_c3(out)
		out = self.lrelu(out)
		context_3 = out # context_3: 1-64-18-23-13

		# Level 4 context pathway
		out = self.conv3d_c4(out) # y: 1-128-9-12-17
		#print("level_4 out size", out.size())
		residual_4 = out
		out = self.norm_lrelu_conv_c4(out)
		out = self.dropout3d(out)
		out = self.norm_lrelu_conv_c4(out)
		out += residual_4
		out = self.inorm3d_c4(out)
		out = self.lrelu(out)
		context_4 = out

#		pdb.set_trace()
		# Level 5
		out = self.conv3d_c5(out) # y: 1-256-5-6-4
		#print("level_5 out size", out.size())
		residual_5 = out
#		print('residual_5:', residual_5.size())

		out = self.norm_lrelu_conv_c5(out) # 1-256-5-6-4
		#print('out_1:', out.size())
		out = self.dropout3d(out)
		out = self.norm_lrelu_conv_c5(out) # 1-256-5-6-4
		#print('out_2:', out.size())        
		out += residual_5
		out = self.norm_lrelu_upscale_conv_norm_lrelu_l0(out) # y: 1-128-24-28-16
        ##ap 
		#print("context_4:", context_4.size())
		out = F.interpolate(out, context_4.size()[2:], mode='nearest')# y: 1-128-9-12-7
		#print('out_3:', out.size())        

		out = self.conv3d_l0(out)
		# print('out_4:', out.size())        
		out = self.inorm3d_l0(out)
		out = self.lrelu(out)
		#print('out_5:', out.size()) 
        
		# Level 1 localization pathway
#		print("out_6: ", out.size(), '\ncontext_4:', context_4.size())
		out = torch.cat([out, context_4], dim=1) #
		out = self.conv_norm_lrelu_l1(out)
		out = self.conv3d_l1(out) #y : 1-128-23-28-15
		out = self.norm_lrelu_upscale_conv_norm_lrelu_l1(out) #y 1-64-18-24-14

		# Level 2 localization pathway
		# print("out_7: ", out.size(), '\ncontext_3:', context_3.size()) # torch.Size([2, 64, 46, 56, 30]) 
		out = F.interpolate(out, context_3.size()[2:], mode='nearest') #context_3: torch.Size([2, 64, 18, 23, 13])
		#print("out_7: ", out.size(), '\ncontext_3:', context_3.size()) # torch.Size([2, 64, 46, 56, 30])
		#print("context_3:", context_3.size())   

		out = torch.cat([out, context_3], dim=1) # y: 1-128-45-55-30
		out = self.conv_norm_lrelu_l2(out)
		ds2 = out # y: 1-128-45-55-30
		out = self.conv3d_l2(out)
		out = self.norm_lrelu_upscale_conv_norm_lrelu_l2(out) # y: 1-32-90-110-60

		# print("before inpter out_8: ", out.size(), '\ncontext_2:', context_3.size()) # torch.Size([2, 64, 46, 56, 30])


		#out = F.interpolate(out, context_2.size()[2:], mode='nearest')
		# print("after inpter out_8: ", out.size(), '\ncontext_2:', context_3.size()) # torch.Size([2, 64, 46, 56, 30])

#		import pdb as pd
#		pd.set_trace()

		# Level 3 localization pathway
		# print("out_8: ", out.size(), '\ncontext_2:', context_2.size()) # torch.Size([2, 64, 46, 56, 30])
		out = F.interpolate(out, context_2.size()[2:], mode='nearest')
		out = torch.cat([out, context_2], dim=1) # y: 1-64-90-110-60
		#print("context_2:", context_2.size())        
		out = self.conv_norm_lrelu_l3(out)
		ds3 = out
		out = self.conv3d_l3(out)# y: 1-32-90-110-60
		out = self.norm_lrelu_upscale_conv_norm_lrelu_l3(out)# y: 1-16-180-220-120

		# Level 4 localization pathway
		#print("out_7: ", out.size(), '\ncontext_1:', context_1.size()) 
		out = torch.cat([out, context_1], dim=1) # y: 1-32-180-220-120
		#print("context_1:", context_1.size())         
		out = self.conv_norm_lrelu_l4(out) # y: 1-32-180-220-120

		out_pred = self.conv3d_l4(out) # out_pred: 1-3-180-220-120
#		import pdb as pd
#		pd.set_trace()


		ds2_1x1_conv = self.ds2_1x1_conv3d(ds2) #y: 1-3-45-55-30
		ds1_ds2_sum_upscale = self.upsacle(ds2_1x1_conv) #y: 1-3-90-110-60
		ds3_1x1_conv = self.ds3_1x1_conv3d(ds3)# y: 1-3-90-110-60
		ds1_ds2_sum_upscale = F.interpolate(ds1_ds2_sum_upscale, ds3_1x1_conv.size()[2:], mode='nearest')

		#print("ds1_ds2_sum_upscale:", ds1_ds2_sum_upscale.size())
		#print("ds3_1x1_conv:", ds3_1x1_conv.size())

		ds1_ds2_sum_upscale_ds3_sum = ds1_ds2_sum_upscale + ds3_1x1_conv# y: 1-3-90-110-60
		ds1_ds2_sum_upscale_ds3_sum_upscale = self.upsacle(ds1_ds2_sum_upscale_ds3_sum)# y: 1-3-180-220-120

		out = out_pred + ds1_ds2_sum_upscale_ds3_sum_upscale# y: 1-3-180-220-120
#		print("out_8: ", out_pred.size(), '\nlast:', ds1_ds2_sum_upscale_ds3_sum_upscale.size())         
#		reg_layer = out
#		out = out.permute(0, 2, 3, 4, 1).contiguous().view(-1, self.n_classes)
		#out = out.view(-1, self.n_classes)
#		out = self.softmax(out)
        # add regression layer
		reg_layer = self.rg4_1x1_conv3d(out)# y: 1-3-180-220-120
#		print("\tIn Model: input size", x.size(),
#              "output size", reg_layer.size())        
        
		return reg_layer