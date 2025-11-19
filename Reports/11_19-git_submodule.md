# 📥 Adding Demucs as a Git Submodule

## 1 Manual Method (Edit .gitmodules)

Add the following block to your project's **`.gitmodules`** file:

```ini
[submodule "external/demucs"]
	path = external/demucs
	url = [https://github.com/facebookresearch/demucs](https://github.com/facebookresearch/demucs)
````

Then, run the command to initialize and fetch the content:

```bash
git submodule update --recursive --init
```

-----

## 2 Recommended Method (Single Command)

Use the following command, which automatically updates `.gitmodules` and fetches the repository:

```bash
git submodule add [https://github.com/facebookresearch/demucs](https://github.com/facebookresearch/demucs) external/demucs
```
