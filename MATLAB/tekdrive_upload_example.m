accessKey = 'qWIfQh6QlKUZZhvGb96Am9R7kx1SCfvd6VzRabek9zYU2gE5';
parentFolderId = '700846a8-5036-48cb-b895-78e7ddb38134';

%Create simple Example File
exampleFileName = 'MatlabTestSine.csv';
t = (0:.1:100); 
sine = sin(t); 
sineData = [t;sine];
sineData = transpose(sineData);
csvwrite(exampleFileName,sineData);


%Example API calls - Get Directory and create/upload file
api = 'https://drive.api.tekcloud.com/';

%Get Directory Tree
url = [api 'tree'];
options = weboptions('HeaderFields',{'X-IS-AK' accessKey},...
                     'RequestMethod','get');
directoryTree = webread(url,options);%%
    
%Create File (preparing for Upload)
url = [api 'file'];
options = weboptions('HeaderFields',{'X-IS-AK' accessKey},...
                     'MediaType','application/json',...
                     'RequestMethod','post');
body = struct('name',exampleFileName,...
              'parentFolderId',parentFolderId);
response = webwrite(url,body,options);

%Upload file to Upload URL
file = fopen(exampleFileName,'r');
data = char(fread(file)');
fclose(file);

url = response.uploadUrl;
options = weboptions('HeaderFields',{'Content-Type' 'application/octet-stream'},...\
                     'MediaType','application/octet-stream',...
                     'CharacterEncoding','ISO-8859-1',...
                     'RequestMethod','put');

response = webwrite(url,data,options);