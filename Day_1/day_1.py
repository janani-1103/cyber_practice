import argparse
import PyPDF2
def decrypt(file_path):
    pdf_name = file_path
    with open(pdf_name,'rb') as file: 
        reader=PyPDF2.PdfReader(file) 
        metadata = reader.metadata 
        for key in metadata:
            print(f"{key}:{metadata[key]}")
        
def encrypt(file_path,key,message,output_file):
    pdf_name = file_path
    with open(pdf_name,'rb') as file:
        reader=PyPDF2.PdfReader(file)
        writer=PyPDF2.PdfWriter()
        writer.append_pages_from_reader(reader)
        metadata = reader.metadata
        metadata.update({key:message})
        writer.add_metadata(metadata)
    with open(file_path,'wb') as output_file:
        writer.write(output_file)
        print('Successfully hidden the message.')

def main():
    parser = argparse.ArgumentParser(description="Program to append the user defined data to the pdf's metadata or to read the metadata")
    
    parser.add_argument('-d',action='store_true',help="Option to decrypt")
    parser.add_argument('-e',action='store_true',help="Option to encrypt")
    parser.add_argument('-f',required=True,type=str,help="File path")
    parser.add_argument('-o',required=False,type=str,help="Output file path")
    parser.add_argument('-mn',required=False,type=str,help="Metadata key value")
    parser.add_argument('-m',required=False,type=str,help="The message you want to hide in the PDF's metadata")
    
    args=parser.parse_args()
    
    if not(args.d or args.e):
        parser.error("The program requires either a -d or -e flag.")
    if args.d:
        decrypt(args.f)
    elif args.e:
        if args.o and args.mn and args.m:
            encrypt(args.f,args.mn,args.m,args.o)
        else:
             parser.error("The program requires the -o, -mn and -m falgs to encrypt.")
 
if __name__ == "__main__":
    main()