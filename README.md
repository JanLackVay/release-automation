To use this from your machine you need to create your own atlassian api token: https://id.atlassian.com/manage-profile/security/api-tokens.
Create an atlassian folder to store your credentials:
```
mkdir ~/.atlassian
cd ~/.atlassian
echo "atl_addr: https://vayio.atlassian.net" > conf.yaml
echo "atl_user:" <user.email> >> conf.yaml
echo "atl_pass:" <user.token> >> conf.yaml
```
Replace the `user.email` with you e mail and the `user.token` with your token.