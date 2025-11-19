# ⚡ Quick Deploy Reference

## 🚀 First Time Setup

```bash
# 1. Test SSH connection (optional but recommended)
./test_ssh_connection.sh

# 2. Run setup wizard
./vastai_setup.sh

# 3. Deploy!
./deploy_vastai.sh
```

## 📋 Daily Commands

```bash
# Deploy/Update
./deploy_vastai.sh

# Check Status
./vastai_status.sh

# View Logs
./vastai_logs.sh

# Restart
./vastai_restart.sh
```

## 🔧 Configuration

### Set Instance ID

**Option 1**: Setup wizard (easiest)
```bash
./vastai_setup.sh
```

**Option 2**: Edit config
```bash
nano vastai_config.json
# Set: "instance_id": "YOUR_ID"
```

**Option 3**: Environment variable
```bash
export VAST_INSTANCE_ID=12345
```

### Customize for Your GPU

Edit `.env`:

```bash
# RTX 3090 (24GB)
MAX_CONCURRENT_JOBS=1

# RTX 4090 (24GB)  
MAX_CONCURRENT_JOBS=2

# A6000 (48GB)
MAX_CONCURRENT_JOBS=3

# A100 (40GB)
MAX_CONCURRENT_JOBS=3
```

## 🆘 Troubleshooting

### SSH Connection Failed
```bash
# Test connection
./test_ssh_connection.sh

# Check instances
vastai show instances

# Verify API key
vastai set api-key YOUR_KEY
```

### Container Won't Start
```bash
# Check logs
./vastai_logs.sh

# Common fixes:
# 1. Reduce MAX_CONCURRENT_JOBS in .env
# 2. Add HF_TOKEN to .env
# 3. Check GPU memory
```

### API Not Responding
```bash
# Check status
./vastai_status.sh

# Wait for model download (first time: 5-10 min)
# Check logs for progress
./vastai_logs.sh
```

## 📊 After Deployment

Your API will be available at:
- **API**: `http://YOUR_IP:7860`
- **Docs**: `http://YOUR_IP:7860/docs`
- **Health**: `http://YOUR_IP:7860/health`

Test it:
```bash
curl http://YOUR_IP:7860/health
```

## 💡 Tips

1. **First deployment**: Takes 5-10 minutes (model download)
2. **Subsequent deploys**: Much faster (uses cached model)
3. **Enable warmup**: Set `WARMUP_ENABLED=true` in `.env`
4. **Monitor GPU**: Use `./vastai_status.sh` regularly
5. **Save costs**: Stop instance when not in use

## 📚 More Help

- Full guide: [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)
- Automation docs: [VASTAI_AUTOMATION_README.md](VASTAI_AUTOMATION_README.md)
- Manual deployment: [VASTAI_DEPLOYMENT.md](VASTAI_DEPLOYMENT.md)

