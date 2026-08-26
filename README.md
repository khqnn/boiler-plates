# boiler-plates

### GIT Setup
#### Add SSH key to agent
```bash
eval $(ssh-agent)
ssh-add ~/.ssh/id_ed25519
```
#### Tell Git to use SSH for signing
```bash
git config --global gpg.format ssh
```
#### Specify which SSH key to use for signing
```bash
git config --global user.signingkey ~/.ssh/your_signing_key
```
#### Optional: Sign all commits by default
```bash
git config --global commit.gpgsign true
```
