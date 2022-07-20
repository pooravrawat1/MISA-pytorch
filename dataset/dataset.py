import os, sys
import numpy as np
import nibabel as nib
import torch
import torch.utils.data as data
import scipy.io as sio

class Dataset(data.Dataset):
    def __init__(self,
        data_in=None,
        num_modal=3):
        super(Dataset, self).__init__()

        self.data_in=data_in
        self.num_modal=num_modal
        self.mat_data=[]

        if isinstance(data_in, type(None)):
            self.data_dir=None
            self.data_files=None
        else:
            if isinstance(data_in, str) and os.path.isdir(data_in):
                self.data_dir=data_in
                self.data_files=os.listdir(data_in)
                self.data_files.sort()
            elif isinstance(data_in, str) and os.path.isfile(data_in):
                data_dir, data_file=os.path.split(data_in)
                self.data_dir=data_dir
                self.data_files=[data_file]
                if '.mat' in data_file:
                    self.mat_data=[i.T for _, i in enumerate(np.squeeze(sio.loadmat(self.data_in)['X']))] # (3,); mat_data[0]: (16,20k)
                    self.num_modal=len(self.mat_data)
            else:
                print("Invalid data_in")
                sys.exit(1)

    def __len__(self):
        if self.mat_data != []:
            return self.mat_data[0].shape[0]
        return len(self.data_files)

    def __getitem__(self, index):
        def load_nii(mri_dir, mri_file):
            mri_nii=nib.load(os.path.join(mri_dir, mri_file))
            mri=np.array(mri_nii.get_fdata(), dtype=np.float32)
            # 0-1 Normalization
            # mri=(mri-mri.min())/(mri.max()-mri.min())
            mri=torch.from_numpy(mri)
            return mri_nii, mri

        data_out=list()
        if self.mat_data == []:
            # .nii file
            _, mri=load_nii(self.data_dir, self.data_files[index])
            data_out.append(mri)
        else:
            # .mat file
            for i in range(self.num_modal):
                data_out.append(torch.from_numpy(self.mat_data[i][index,:]))

        return data_out

if __name__ == '__main__':
    rootpath="/Users/xli77/Documents/MISA-pytorch/simulation_data"
    ds=Dataset(data_in=os.path.join(rootpath,"sim_siva.mat"))
    dl=data.DataLoader(dataset=ds, batch_size=1000, shuffle=True)
    for i, data_in in enumerate(dl):
        # import pdb; pdb.set_trace()
        print(len(data_in), data_in[0].shape)