#!/usr/bin/env bash

KUBE_NAMESPACE='picnic'
NGINX_POD_NAME=$(kubectl get pods -n $KUBE_NAMESPACE --selector=app=nginx-ingress,component=controller -o name | cut -f1 -d' ')

kubectl exec -n "$KUBE_NAMESPACE" "$NGINX_POD_NAME" -- cat '/etc/nginx/nginx.conf'