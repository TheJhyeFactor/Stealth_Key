import base64

incoming = input("qjcLsXMD3m+WgJng3+ViQTjUWl8p6D/YrWRezJVeVare1LQ2wrCR8EGWPXsHVCp25ykvZ8mVUkDRIQAX8MFu8pgawERiHSbZPU60L//qNa3nKS9nyZVSQNEhABfwwW7yr48ZV1LVN0fClgBSPB5vo1x7+xJPX3lKdHGrqIyJauHD7+ERI5sPcMPwJ5bN784dXHv7Ek9feUp0cauojIlq4UEeVDwa6nQJFNyhT9BkEH46xyZ26yxObBV2ujc43chtoM64Q8UW8K3+xMDJrTktVg==")
original = base64.b64decode(incoming[::-1].encode()).decode()
print(original)